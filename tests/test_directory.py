import os.path
import pytest

from icedrive_blob.blob import BlobService

import configparser

CONFIG = configparser.ConfigParser()
CONFIG.read("config/app.ini")
BLOB_DIRECTORY = CONFIG["Blobs"]["blob_directory"]

def test_directory_creation():
    """Test directory didn't exist and is created when instantiating a Blob Service."""
    if os.path.exists(BLOB_DIRECTORY):
        pytest.skip("Directory already exists")

    BlobService(BLOB_DIRECTORY)

    assert os.path.exists(BLOB_DIRECTORY)
    

def test_directory_inst_altered():
    """Test if the directory doesn't change if it already exists.
    It should not change because it should not be created again nor add or remove files."""
    if not os.path.exists(BLOB_DIRECTORY):
        pytest.skip("Directory does not exist")

    last_mod = os.path.getmtime(BLOB_DIRECTORY)
    BlobService(BLOB_DIRECTORY)

    assert last_mod == os.path.getmtime(BLOB_DIRECTORY)
