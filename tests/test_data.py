import os
import pytest
import hashlib
import configparser

CONFIG = configparser.ConfigParser()
CONFIG.read("config/app.ini")

def test_all_blobs_are_linked():
    """Test if all blobs are linked when instantiating a Blob Service."""

    blobs_directory = CONFIG["Blobs"]["blobs_directory"]
    links_directory = CONFIG["Blobs"]["links_directory"]

    if not os.path.exists(blobs_directory) or not os.path.exists(links_directory):
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
