"""Module for servants implementations."""
import hashlib
import os
import uuid
import logging
from typing import Callable, Any

import Ice

import IceDrive

from .discovery import Discovery

class DataTransfer(IceDrive.DataTransfer):
    """Implementation of an IceDrive.DataTransfer interface."""
    def __init__(self, blob_path: str):
        self.f = open(blob_path, "rb")

    def read(self, size: int, current: Ice.Current = None) -> bytes:
        """Returns a list of bytes from the opened file."""
        try:
            return self.f.read(size)
        except IOError:
            raise IceDrive.FailedToReadData()

    def close(self, current: Ice.Current = None) -> None:
        """Close the currently opened file."""
        self.f.close()
        if current:
            current.adapter.remove(current.id)


class BlobService(IceDrive.BlobService):
    """Implementation of an IceDrive.BlobService interface."""
    def __init__(self, query_prx: IceDrive.BlobQueryPrx, discovery_servant: Discovery, blobs_directory: str, links_directory: str, data_transfer_size: int, partial_uploads_directory: str):
        self.query_prx = query_prx
        self.discovery_servant = discovery_servant
        if blobs_directory == links_directory or blobs_directory == partial_uploads_directory or links_directory == partial_uploads_directory:
            raise ValueError("Store directories must be different")

        if not isinstance(data_transfer_size, int):
            raise TypeError("data_transfer_size must be an integer")

        if data_transfer_size <= 0:
            raise ValueError("data_transfer_size must be greater than 0")

        self.blobs_directory = blobs_directory
        self.links_directory = links_directory
        self.partial_uploads_directory = partial_uploads_directory

        # make sure the directories exist
        os.makedirs(self.blobs_directory, exist_ok=True)
        os.makedirs(self.links_directory, exist_ok=True)
        os.makedirs(self.partial_uploads_directory, exist_ok=True)

        logging.debug("BlobService: using directories: %s %s %s", self.blobs_directory, self.links_directory, self.partial_uploads_directory)

        # read the links of each blob
        self.blobs = {blob_id: self.read_blob_links(blob_id) for blob_id in os.listdir(self.blobs_directory)}

        logging.info("BlobService: loaded %d blobs", len(self.blobs))

        self.data_transfer_size = data_transfer_size

        self.clean_partial_uploads()

        logging.debug("BlobService: cleaned partial uploads")

    def read_blob_links(self, blob_id: str) -> int:
        """Read the number of links of a blob_id file."""
        with open(os.path.join(self.links_directory, blob_id), "r") as f:
            return int(f.read())

    def clean_partial_uploads(self) -> None:
        """Remove all partial uploads. Only needed if the service was closed while uploading."""
        for filename in os.listdir(self.partial_uploads_directory):
            os.remove(os.path.join(self.partial_uploads_directory, filename))

    @staticmethod
    def ask_for_help(help_function: Callable[[str, IceDrive.BlobQueryResponsePrx], None], blob_id: str, adapter: Ice.ObjectAdapterI) -> Any:
        """Ask for help to other instances to find a blob_id."""
        future = Ice.Future()
        from .delayed_response import BlobQueryResponse
        response = BlobQueryResponse(future)
        response_prx = adapter.addWithUUID(response)
        response_prx = IceDrive.BlobQueryResponsePrx.uncheckedCast(response_prx)
        logging.info("BlobService: querying other instances for blob: %s, waiting response on: %s", blob_id, response_prx)
        help_function(blob_id, response_prx)

        try:
            result = future.result(5)
        except Ice.TimeoutException:
            raise IceDrive.UnknownBlob(blob_id)

        adapter.remove(response_prx.ice_getIdentity())

        return result

    def link(self, blob_id: str, current: Ice.Current = None) -> None:
        """Mark a blob_id file as linked in some directory."""
        try:
            self.blobs[blob_id] += 1
            with open(os.path.join(self.links_directory, blob_id), "w") as f:
                f.write(str(self.blobs[blob_id]))
        except KeyError:
            if not current:
                raise IceDrive.UnknownBlob(blob_id)

            BlobService.ask_for_help(self.query_prx.linkBlob, blob_id, current.adapter)


    def unlink(self, blob_id: str, current: Ice.Current = None) -> None:
        """Mark a blob_id as unlinked (removed) from some directory."""
        try:
            self.blobs[blob_id] -= 1
            if self.blobs[blob_id] < 1:
                os.remove(os.path.join(self.blobs_directory, blob_id))
                os.remove(os.path.join(self.links_directory, blob_id))
                del self.blobs[blob_id]
                logging.info("BlobService: removed blob %s", blob_id)
            else:
                with open(os.path.join(self.links_directory, blob_id), "w") as f:
                    f.write(str(self.blobs[blob_id]))
        except KeyError:
            if not current:
                raise IceDrive.UnknownBlob(blob_id)

            BlobService.ask_for_help(self.query_prx.unlinkBlob, blob_id, current.adapter)

    def upload(
        self, user: IceDrive.UserPrx, blob: IceDrive.DataTransferPrx, current: Ice.Current = None
    ) -> str:
        """Register a DataTransfer object to upload a file to the service."""
        if not self.discovery_servant.getAtuhencticationService().verifyUser(user):
            raise IceDrive.FailedToReadData

        tmp_filename = str(uuid.uuid4())
        tmp_path = os.path.join(self.partial_uploads_directory, tmp_filename)
        sha256 = hashlib.sha256()

        logging.debug("BlobService: started uploading blob %s", tmp_filename)

        try:
            with open(tmp_path, "wb") as f:
                still_uploading = True
                while still_uploading and user.isAlive():
                    read_data = blob.read(self.data_transfer_size)
                    sha256.update(read_data)
                    f.write(read_data)
                    still_uploading = len(read_data) == self.data_transfer_size

            blob.close()
        except IOError:
            raise IceDrive.FailedToReadData()

        if still_uploading:
            raise IceDrive.FailedToReadData()

        # Compute the blob_id
        blob_id = sha256.hexdigest()

        try:
            if not current:
                raise IceDrive.UnknownBlob(blob_id)
            # or no one has the blob
            BlobService.ask_for_help(self.query_prx.blobIdExists, blob_id, current.adapter)
            os.remove(tmp_path)
        except IceDrive.UnknownBlob:
            # Rename the blob file
            os.rename(tmp_path, os.path.join(self.blobs_directory, blob_id))

            # Store the link file, as 0 links, it hasn't been explicitly linked yet, but we need a link file of this blob
            self.blobs[blob_id] = -1
            self.link(blob_id)

        logging.info("BlobService: finished uploading blob %s", blob_id)

        return blob_id

    def download(
        self, user: IceDrive.UserPrx, blob_id: str, current: Ice.Current = None
    ) -> IceDrive.DataTransferPrx:
        """Return a DataTransfer objet to enable the client to download the given blob_id."""
        if user and not self.discovery_servant.getAtuhencticationService().verifyUser(user):
            raise IceDrive.FailedToReadData

        if blob_id not in self.blobs:
            raise IceDrive.UnknownBlob(blob_id)

        servant = DataTransfer(os.path.join(self.blobs_directory, blob_id))
        prx = current.adapter.addWithUUID(servant) if current else None

        logging.info("BlobService: created DataTransfer for blob %s at %s", blob_id, prx)

        return IceDrive.DataTransferPrx.uncheckedCast(prx) if current else servant

