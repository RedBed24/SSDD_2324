import pytest
import os
import Ice

from icedrive_blob.blob import DataTransfer, BlobService

MOCK_BLOBS_DIRECTORY = "/tmp/ssdd/mock/blobs_directory"
MOCK_LINKS_DIRECTORY = "/tmp/ssdd/mock/links_directory"

def test_invalid_data_transfer_size():
    with pytest.raises(ValueError):
        BlobService(MOCK_BLOBS_DIRECTORY, MOCK_LINKS_DIRECTORY, 0)


def test_upload():
    """Test if the upload method works as expected."""

    # Mock DataTransfer
    class MockDataTransfer(DataTransfer):
        def __init__(self, data: bytes):
            self.data = data

        def read(self, size: int, current: Ice.Current = None) -> bytes:
            return self.data[:size]

        def close(self, current: Ice.Current = None) -> None:
            pass

    # Mock DataTransfer object
    data = b"Hello World"
    blob = MockDataTransfer(data)

    # Create BlobService
    blob_service = BlobService(MOCK_BLOBS_DIRECTORY, MOCK_LINKS_DIRECTORY, 1024)

    # Upload
    blob_id = blob_service.upload(blob)

    # Check if the blob_id file exists
    assert os.path.exists(os.path.join(MOCK_BLOBS_DIRECTORY, blob_id))

    # Check if the blob_id file contains the data
    with open(os.path.join(MOCK_BLOBS_DIRECTORY, blob_id), "rb") as f:
        assert f.read() == data

    # Check if the blob_id file has 1 link
    with open(os.path.join(MOCK_LINKS_DIRECTORY, blob_id), "r") as f:
        assert f.read() == "1"

    # Remove the directories
    os.remove(os.path.join(MOCK_BLOBS_DIRECTORY, blob_id))
    os.remove(os.path.join(MOCK_LINKS_DIRECTORY, blob_id))
    os.rmdir(MOCK_BLOBS_DIRECTORY)
    os.rmdir(MOCK_LINKS_DIRECTORY)
