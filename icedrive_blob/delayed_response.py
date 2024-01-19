"""Servant implementation for the delayed response mechanism."""

import logging

import Ice

import IceDrive


class BlobQueryResponse(IceDrive.BlobQueryResponse):
    """Query response receiver."""
    def __init__(self, future: Ice.Future):
        self.future = future

    def downloadBlob(self, blob: IceDrive.DataTransferPrx, current: Ice.Current = None) -> None:
        """Receive a `DataTransfer` when other service instance knows the `blob_id`."""
        self.future.set_result(blob)

    def blobExists(self, current: Ice.Current = None) -> None:
        """Indicate that `blob_id` was recognised by other service instance."""
        self.future.set_result(None)

    def blobLinked(self, current: Ice.Current = None) -> None:
        """Indicate that `blob_id` was recognised by other service instance and was linked."""
        self.future.set_result(None)

    def blobUnlinked(self, current: Ice.Current = None) -> None:
        """Indicate that `blob_id` was recognised by other service instance and was unlinked."""
        self.future.set_result(None)


class BlobQuery(IceDrive.BlobQuery):
    """Query receiver."""
    from .blob import BlobService

    def __init__(self, blob_servant: BlobService) -> None:
        self.blob_servant = blob_servant

    def downloadBlob(self, blob_id: str, response: IceDrive.BlobQueryResponsePrx, current: Ice.Current = None) -> None:
        """Receive a query for downloading an archive based on `blob_id`."""
        logging.debug("BlobQuery: received download query for blob %s", blob_id)
        if blob_id in self.blob_servant.blobs:
            response.downloadBlob(self.blob_servant.download(None, blob_id))

    def blobIdExists(self, blob_id: str, response: BlobQueryResponse, current: Ice.Current = None) -> None:
        """Receive a query to check if `blob_id` exists."""
        logging.debug("BlobQuery: received blobIdExists query for blob %s", blob_id)
        if blob_id in self.blob_servant.blobs:
            response.blobExists()

    def linkBlob(self, blob_id: str, response: IceDrive.BlobQueryResponsePrx, current: Ice.Current = None) -> None:
        """Receive a query to create a link for `blob_id` archive if it exists."""
        logging.debug("BlobQuery: received link query for blob %s", blob_id)
        if blob_id in self.blob_servant.blobs:
            self.blob_servant.link(blob_id)
            response.blobLinked()

    def unlinkBlob(self, blob_id: str, response: IceDrive.BlobQueryResponsePrx, current: Ice.Current = None) -> None:
        """Receive a query to destroy a link for `blob_id` archive if it exists."""
        logging.debug("BlobQuery: received unlink query for blob %s", blob_id)
        if blob_id in self.blob_servant.blobs:
            self.blob_servant.unlink(blob_id)
            response.blobUnlinked()

