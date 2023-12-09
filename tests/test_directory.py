import os.path
import pytest

from icedrive_blob.blob import BlobService

import configparser

CONFIG = configparser.ConfigParser()
CONFIG.read("config/app.ini")

def test_directory_creation():
    """Test directory didn't exist and is created when instantiating a Blob Service."""

    # Mock directories
    test_blobs_directory = "tmp/blobs_directory"
    test_links_directory = "tmp/links_directory"

    if os.path.exists(test_blobs_directory) or os.path.exists(test_links_directory):
        pytest.skip("Directories already exists")

    BlobService(test_blobs_directory, test_links_directory, 0)

    assert os.path.exists(test_blobs_directory) and os.path.exists(test_links_directory)

    # Can remove the directories because they are empty, they were just created
    os.rmdir(test_blobs_directory)
    os.rmdir(test_links_directory)


def test_directory_inst_altered():
    """Test if the directory doesn't change if it already exists.
    It should not change because it should not be created again nor add or remove files."""

    blobs_directory = CONFIG["Blobs"]["blobs_directory"]
    links_directory = CONFIG["Blobs"]["links_directory"]

    if not os.path.exists(blobs_directory) and not os.path.exists(links_directory):
        pytest.skip("Directories do not exist")

    blob_last_mod = os.path.getmtime(blobs_directory)
    link_last_mod = os.path.getmtime(blobs_directory)
    BlobService(blobs_directory, links_directory, 0)

    assert blob_last_mod == os.path.getmtime(blobs_directory) and link_last_mod == os.path.getmtime(links_directory)

