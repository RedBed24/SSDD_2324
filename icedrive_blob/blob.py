"""Module for servants implementations."""
import hashlib
import os
import uuid

import Ice

import IceDrive


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


class BlobService(IceDrive.BlobService):
    """Implementation of an IceDrive.BlobService interface."""
    def __init__(self, blobs_directory: str, links_directory: str, data_transfer_size: int, partial_uploads_directory: str):
        if blobs_directory == links_directory or blobs_directory == partial_uploads_directory or links_directory == partial_uploads_directory:
            raise ValueError("Store directories must be different")

        if data_transfer_size <= 0:
            raise ValueError("data_transfer_size must be greater than 0")

        self.blobs_directory = blobs_directory
        self.links_directory = links_directory
        self.partial_uploads_directory = partial_uploads_directory

        # make sure the directories exist
        os.makedirs(self.blobs_directory, exist_ok=True)
        os.makedirs(self.links_directory, exist_ok=True)
        os.makedirs(self.partial_uploads_directory, exist_ok=True)

        # read the links of each blob
        self.blobs = {blob_id: self.read_blob_links(blob_id) for blob_id in os.listdir(self.blobs_directory)}

        self.data_transfer_size = data_transfer_size

        self.clean_partial_uploads()
    
    def read_blob_links(self, blob_id: str) -> int:
        """Read the number of links of a blob_id file."""
        with open(os.path.join(self.links_directory, blob_id), "r") as f:
            return int(f.read())

    def clean_partial_uploads(self) -> None:
        """Remove all partial uploads. Only needed if the service was closed while uploading."""
        for filename in os.listdir(self.partial_uploads_directory):
            os.remove(os.path.join(self.partial_uploads_directory, filename))

    def link(self, blob_id: str, current: Ice.Current = None) -> None:
        """Mark a blob_id file as linked in some directory."""
        try:
            self.blobs[blob_id] += 1
        except KeyError:
            raise IceDrive.UnknownBlob()

        with open(os.path.join(self.links_directory, blob_id), "w") as f:
            f.write(str(self.blobs[blob_id]))

    def unlink(self, blob_id: str, current: Ice.Current = None) -> None:
        """Mark a blob_id as unlinked (removed) from some directory."""
        try:
            self.blobs[blob_id] -= 1
            if self.blobs[blob_id] < 1:
                os.remove(os.path.join(self.blobs_directory, blob_id))
                os.remove(os.path.join(self.links_directory, blob_id))
                del self.blobs[blob_id]
            else:
                with open(os.path.join(self.links_directory, blob_id), "w") as f:
                    f.write(str(self.blobs[blob_id]))
        except KeyError:
            raise IceDrive.UnknownBlob()

    def upload(
        self, blob: IceDrive.DataTransferPrx, current: Ice.Current = None
    ) -> str:
        """Register a DataTransfer object to upload a file to the service."""
        tmp_filename = str(uuid.uuid4())
        sha256 = hashlib.sha256()

        with open(os.path.join(self.partial_uploads_directory, tmp_filename), "wb") as f:
            still_uploading = True
            while still_uploading:
                read_data = blob.read(self.data_transfer_size)
                sha256.update(read_data)
                f.write(read_data)
                still_uploading = len(read_data) == self.data_transfer_size

        blob.close()

        # Compute the blob_id
        blob_id = sha256.hexdigest()

        # Rename the blob file
        os.rename(os.path.join(self.partial_uploads_directory, tmp_filename), os.path.join(self.blobs_directory, blob_id))

        # Store the link file
        self.blobs[blob_id] = 0
        self.link(blob_id)

        return blob_id

    def download(
        self, blob_id: str, current: Ice.Current = None
    ) -> IceDrive.DataTransferPrx:
        """Return a DataTransfer objet to enable the client to download the given blob_id."""
        try:
            self.blobs[blob_id]
        except KeyError:
            raise IceDrive.UnknownBlob()

        return DataTransfer(os.path.join(self.blobs_directory, blob_id))

