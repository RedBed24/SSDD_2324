import os.path
import pytest

from icedrive_blob.blob import BlobService

MOCK_BLOBS_DIRECTORY = "/tmp/ssdd/mock/blobs_directory"
MOCK_LINKS_DIRECTORY = "/tmp/ssdd/mock/links_directory"
MOCK_PARTIAL_UPLOADS_DIRECTORY = "/tmp/ssdd/mock/partial_uploads_directory"

def clean():
    # Can remove the directories because they are empty, they were just created
    os.rmdir(MOCK_BLOBS_DIRECTORY)
    os.rmdir(MOCK_LINKS_DIRECTORY)
    os.rmdir(MOCK_PARTIAL_UPLOADS_DIRECTORY)


def test_directory_creation():
    """Test directory didn't exist and is created when instantiating a Blob Service."""

    if os.path.exists(MOCK_BLOBS_DIRECTORY) or os.path.exists(MOCK_LINKS_DIRECTORY) or os.path.exists(MOCK_PARTIAL_UPLOADS_DIRECTORY):
        pytest.skip("Directories already exists")

    BlobService(None, MOCK_BLOBS_DIRECTORY, MOCK_LINKS_DIRECTORY, 1, MOCK_PARTIAL_UPLOADS_DIRECTORY)

    assert os.path.exists(MOCK_BLOBS_DIRECTORY) and os.path.exists(MOCK_LINKS_DIRECTORY) and os.path.exists(MOCK_PARTIAL_UPLOADS_DIRECTORY)

    clean()


def test_directory_inst_altered():
    """Test if the directory doesn't change if it already exists.
    It should not change because it should not be created again nor add or remove files."""

    os.makedirs(MOCK_BLOBS_DIRECTORY, exist_ok=True)
    os.makedirs(MOCK_LINKS_DIRECTORY, exist_ok=True)
    os.makedirs(MOCK_PARTIAL_UPLOADS_DIRECTORY, exist_ok=True)

    blob_last_mod = os.path.getmtime(MOCK_BLOBS_DIRECTORY)
    link_last_mod = os.path.getmtime(MOCK_LINKS_DIRECTORY)

    BlobService(None, MOCK_BLOBS_DIRECTORY, MOCK_LINKS_DIRECTORY, 1, MOCK_PARTIAL_UPLOADS_DIRECTORY)

    assert blob_last_mod == os.path.getmtime(MOCK_BLOBS_DIRECTORY) and link_last_mod == os.path.getmtime(MOCK_LINKS_DIRECTORY)

    clean()


def test_partial_uploads_directory_is_cleaned():
    """The partial uploads directory should be cleaned when instantiating a Blob Service."""
    os.makedirs(MOCK_PARTIAL_UPLOADS_DIRECTORY, exist_ok=True)
    with open(os.path.join(MOCK_PARTIAL_UPLOADS_DIRECTORY, "file"), "w") as f:
        f.write("test")

    BlobService(None, MOCK_BLOBS_DIRECTORY, MOCK_LINKS_DIRECTORY, 1, MOCK_PARTIAL_UPLOADS_DIRECTORY)

    assert not len(os.listdir(MOCK_PARTIAL_UPLOADS_DIRECTORY))

    clean()


dir = "tmp"
data = [
    # Same directory
    ((None, dir, dir, 1, dir), ValueError),
    ((None, dir*2, dir, 1, dir), ValueError),
    ((None, dir, dir*2, 1, dir), ValueError),
    ((None, dir, dir, 1, dir*2), ValueError),
    # Invalid data transfer size
    ((None, MOCK_BLOBS_DIRECTORY, MOCK_LINKS_DIRECTORY, 0, MOCK_PARTIAL_UPLOADS_DIRECTORY), ValueError),
    ((None, MOCK_BLOBS_DIRECTORY, MOCK_LINKS_DIRECTORY, 0.5, MOCK_PARTIAL_UPLOADS_DIRECTORY), TypeError),
    # Directory is not a string
    ((None, 1, MOCK_LINKS_DIRECTORY, 1, MOCK_PARTIAL_UPLOADS_DIRECTORY), TypeError),
    ((None, MOCK_BLOBS_DIRECTORY, 1, 1, MOCK_PARTIAL_UPLOADS_DIRECTORY), TypeError),
    ((None, MOCK_BLOBS_DIRECTORY, MOCK_LINKS_DIRECTORY, 1, 1), TypeError),
]

@pytest.mark.parametrize("atributes, expected_exception", data)
def test_blob_service_creation(atributes, expected_exception):
    with pytest.raises(expected_exception):
        BlobService(*atributes)


