import pytest
import os
import hashlib
import Ice

from icedrive_blob.blob import DataTransfer, BlobService
import IceDrive

MOCK_BLOBS_DIRECTORY = "/tmp/ssdd/mock/blobs_directory"
MOCK_LINKS_DIRECTORY = "/tmp/ssdd/mock/links_directory"

DATA = b"Hello World"

def setup() -> str:
    # Mock DataTransfer object
    blob = MockDataTransfer(DATA)

    # Create BlobService
    blob_service = BlobService(MOCK_BLOBS_DIRECTORY, MOCK_LINKS_DIRECTORY, 1024)

    # Upload
    return blob_service, blob_service.upload(blob)

def clean(blob_id: str):
    os.remove(os.path.join(MOCK_BLOBS_DIRECTORY, blob_id))
    os.remove(os.path.join(MOCK_LINKS_DIRECTORY, blob_id))
    os.rmdir(MOCK_BLOBS_DIRECTORY)
    os.rmdir(MOCK_LINKS_DIRECTORY)


class MockDataTransfer(DataTransfer):
    def __init__(self, data: bytes):
        self.data = data

    def read(self, size: int, current: Ice.Current = None) -> bytes:
        return self.data[:size]

    def close(self, current: Ice.Current = None) -> None:
        pass


def test_upload():
    """Test if the upload method works as expected.
    Req # 1, Req # 12"""
    _, blob_id = setup()

    # Check if the blob_id is a valid sha256 hash
    sha256 = hashlib.sha256()
    sha256.update(DATA)
    assert blob_id == sha256.hexdigest()

    # Check if the blob_id file exists
    assert os.path.exists(os.path.join(MOCK_BLOBS_DIRECTORY, blob_id))

    # Check if the blob_id file contains the data
    with open(os.path.join(MOCK_BLOBS_DIRECTORY, blob_id), "rb") as f:
        assert f.read() == DATA

    # Check if the blob_id file has 1 link
    with open(os.path.join(MOCK_LINKS_DIRECTORY, blob_id), "r") as f:
        assert f.read() == "1"

    clean(blob_id)


def test_download():
    """Test if the download method works as expected.
    Req # 2, Req # 10"""
    blob_service, blob_id = setup()

    # Get the data transfer object
    blob = blob_service.download(blob_id) 

    # Check if the blob_id file contains the data
    assert blob.read(1024) == DATA

    blob.close()

    clean(blob_id)


def test_download_with_other_blobservice():
    """Req # 3"""
    blob_service, blob_id = setup()

    blob = blob_service.download(blob_id)
    data = blob.read(1024)
    blob.close()

    # Create another BlobService
    blob_service = BlobService(MOCK_BLOBS_DIRECTORY, MOCK_LINKS_DIRECTORY, 1024)
    
    # Get the data transfer object
    blob = blob_service.download(blob_id)
    # Check if the blob_id file contains the data
    assert blob.read(1024) == data
    blob.close()

    clean(blob_id)


def test_invalid_download():
    """Test if the download method raises an exception when the blob_id is invalid.
    Req # 4"""
    blob_service = BlobService(MOCK_BLOBS_DIRECTORY, MOCK_LINKS_DIRECTORY, 1024)

    with pytest.raises(IceDrive.UnknownBlob):
        blob_service.download("invalid_blob_id")


def test_link():
    """Req # 5"""
    blob_service, blob_id = setup()

    blob_service.link(blob_id)

    # Check if the blob_id file has 2 links
    with open(os.path.join(MOCK_LINKS_DIRECTORY, blob_id), "r") as f:
        assert f.read() == "2"

    clean(blob_id)


def test_link_uknown_blob():
    """Req # 6"""
    blob_service = BlobService(MOCK_BLOBS_DIRECTORY, MOCK_LINKS_DIRECTORY, 1024)

    with pytest.raises(IceDrive.UnknownBlob):
        blob_service.link("invalid_blob_id")


def test_unlink():
    """Req # 7"""
    blob_service, blob_id = setup()

    blob_service.unlink(blob_id)

    # Try to get the blob_id file
    with pytest.raises(IceDrive.UnknownBlob):
        blob_service.download(blob_id)


def test_unlink_uknown_blob():
    """Req # 8"""
    blob_service = BlobService(MOCK_BLOBS_DIRECTORY, MOCK_LINKS_DIRECTORY, 1024)

    with pytest.raises(IceDrive.UnknownBlob):
        blob_service.unlink("invalid_blob_id")


def test_unlinks_deletes():
    """Req # 9"""
    blob_service, blob_id = setup()

    blob_service.unlink(blob_id)

    # Check if the blob_id file does not exist
    assert not os.path.exists(os.path.join(MOCK_BLOBS_DIRECTORY, blob_id))
    assert not os.path.exists(os.path.join(MOCK_LINKS_DIRECTORY, blob_id))

