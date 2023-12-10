import os.path
import pytest

from icedrive_blob.blob import BlobService

MOCK_BLOBS_DIRECTORY = "/tmp/ssdd/mock/blobs_directory"
MOCK_LINKS_DIRECTORY = "/tmp/ssdd/mock/links_directory"
MOCK_PARTIAL_UPLOADS_DIRECTORY = "/tmp/ssdd/mock/partial_uploads_directory"

def test_directory_creation():
    """Test directory didn't exist and is created when instantiating a Blob Service."""

    if os.path.exists(MOCK_BLOBS_DIRECTORY) or os.path.exists(MOCK_LINKS_DIRECTORY) or os.path.exists(MOCK_PARTIAL_UPLOADS_DIRECTORY):
        pytest.skip("Directories already exists")

    BlobService(MOCK_BLOBS_DIRECTORY, MOCK_LINKS_DIRECTORY, 1, MOCK_PARTIAL_UPLOADS_DIRECTORY)

    assert os.path.exists(MOCK_BLOBS_DIRECTORY) and os.path.exists(MOCK_LINKS_DIRECTORY) and os.path.exists(MOCK_PARTIAL_UPLOADS_DIRECTORY)

    # Can remove the directories because they are empty, they were just created
    os.rmdir(MOCK_BLOBS_DIRECTORY)
    os.rmdir(MOCK_LINKS_DIRECTORY)
    os.rmdir(MOCK_PARTIAL_UPLOADS_DIRECTORY)


def test_directory_inst_altered():
    """Test if the directory doesn't change if it already exists.
    It should not change because it should not be created again nor add or remove files."""

    os.makedirs(MOCK_BLOBS_DIRECTORY, exist_ok=True)
    os.makedirs(MOCK_LINKS_DIRECTORY, exist_ok=True)

    blob_last_mod = os.path.getmtime(MOCK_BLOBS_DIRECTORY)
    link_last_mod = os.path.getmtime(MOCK_LINKS_DIRECTORY)

    BlobService(MOCK_BLOBS_DIRECTORY, MOCK_LINKS_DIRECTORY, 1, MOCK_PARTIAL_UPLOADS_DIRECTORY)

    assert blob_last_mod == os.path.getmtime(MOCK_BLOBS_DIRECTORY) and link_last_mod == os.path.getmtime(MOCK_LINKS_DIRECTORY)

    os.rmdir(MOCK_BLOBS_DIRECTORY)
    os.rmdir(MOCK_LINKS_DIRECTORY)


def test_partial_uploads_directory_is_cleaned():
    """The partial uploads directory should be cleaned when instantiating a Blob Service."""
    os.makedirs(MOCK_PARTIAL_UPLOADS_DIRECTORY, exist_ok=True)
    with open(os.path.join(MOCK_PARTIAL_UPLOADS_DIRECTORY, "file"), "w") as f:
        f.write("test")

    BlobService(MOCK_BLOBS_DIRECTORY, MOCK_LINKS_DIRECTORY, 1, MOCK_PARTIAL_UPLOADS_DIRECTORY)

    assert not len(os.listdir(MOCK_PARTIAL_UPLOADS_DIRECTORY))


def test_same_directory():
    """Test if the same directory for blobs and links is not allowed."""
    dir = "tmp"

    with pytest.raises(ValueError):
        BlobService(dir, dir, 1, dir)

    with pytest.raises(ValueError):
        BlobService(dir*2, dir, 1, dir)

    with pytest.raises(ValueError):
        BlobService(dir, dir*2, 1, dir)

    with pytest.raises(ValueError):
        BlobService(dir, dir, 1, dir*2)


def test_invalid_data_transfer_size():
    with pytest.raises(ValueError):
        BlobService(MOCK_BLOBS_DIRECTORY, MOCK_LINKS_DIRECTORY, 0, MOCK_PARTIAL_UPLOADS_DIRECTORY)

