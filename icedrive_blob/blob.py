"""Module for servants implementations."""
import os

import Ice

import IceDrive


class DataTransfer(IceDrive.DataTransfer):
    """Implementation of an IceDrive.DataTransfer interface."""

    def read(self, size: int, current: Ice.Current = None) -> bytes:
        """Returns a list of bytes from the opened file."""

    def close(self, current: Ice.Current = None) -> None:
        """Close the currently opened file."""


class BlobService(IceDrive.BlobService):
    """Implementation of an IceDrive.BlobService interface."""
    def __init__(self, blobs_directory: str, links_directory: str, data_transfer_size: int):
        self.blobs_directory = blobs_directory
        self.links_directory = links_directory

        # make sure the directories exist
        os.makedirs(self.blobs_directory, exist_ok=True)
        os.makedirs(self.links_directory, exist_ok=True)

        # read the links of each blob
        self.blobs = {blob_id: self.read_blob_links(blob_id) for blob_id in os.listdir(self.blobs_directory)}
    
    def read_blob_links(self, blob_id: str) -> int:
        """Read the number of links of a blob_id file."""
        with open(os.path.join(self.links_directory, blob_id), "r") as f:
            return int(f.read())

    def link(self, blob_id: str, current: Ice.Current = None) -> None:
        """Mark a blob_id file as linked in some directory."""

    def unlink(self, blob_id: str, current: Ice.Current = None) -> None:
        """Mark a blob_id as unlinked (removed) from some directory."""

    def upload(
        self, blob: IceDrive.DataTransferPrx, current: Ice.Current = None
    ) -> str:
        """Register a DataTransfer object to upload a file to the service."""

    def download(
        self, blob_id: str, current: Ice.Current = None
    ) -> IceDrive.DataTransferPrx:
        """Return a DataTransfer objet to enable the client to download the given blob_id."""
