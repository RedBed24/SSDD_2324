import os.path
import pytest
import hashlib

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


def test_all_blobs_are_linked():
    """Test if all blobs are linked when instantiating a Blob Service."""

    blobs_directory = CONFIG["Blobs"]["blobs_directory"]
    links_directory = CONFIG["Blobs"]["links_directory"]

    if not os.path.exists(blobs_directory) and not os.path.exists(links_directory):
        pytest.skip("Directories do not exist")

    blobs = os.listdir(blobs_directory)
    links = os.listdir(links_directory)

    # FIXME: files of directories are in same order?
    assert blobs == links


def test_all_links_are_valid():
    """Test if all blobs are valid, i.e, they have at least one link.
    There should be no blobs with 0 links."""

    links_directory = CONFIG["Blobs"]["links_directory"]

    if not os.path.exists(links_directory):
        pytest.skip("Directory does not exist")

    links = os.listdir(links_directory)

    for link in links:
        with open(os.path.join(links_directory, link), "r") as f:
            assert int(f.read()) > 0


def test_blobs_ids_are_valid():
    """Test if all blobs ids are valid, i.e, they are the sha256 hash of their contents."""

    blobs_directory = CONFIG["Blobs"]["blobs_directory"]

    if not os.path.exists(blobs_directory):
        pytest.skip("Directory does not exist")

    blobs = os.listdir(blobs_directory)

    for blob_id in blobs:
        with open(os.path.join(blobs_directory, blob_id), "r") as f:
            sha256 = hashlib.sha256()
            sha256.update(f.read())
            assert blob_id == sha256.hexdigest()


def test_same_directory():
    """Test if the same directory for blobs and links is not allowed."""
    dir = "tmp"

    with pytest.raises(ValueError):
        BlobService(dir, dir, 0)

