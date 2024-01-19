import os
import pytest
import hashlib

#
# THESE TESTS ONLY WORK IF THE BLOB SERVICE HAS RUN AS A SERVICE
# IT IS NOT POSSIBLE TO RUN THESE WITHOUT THE CREATED BLOBS
# TESTS CHECK INTEGRITY OF THE STORED DATA
#

USED_BLOBS_DIRECTORY = "/tmp/ssdd/blobs"
USED_LINKS_DIRECTORY = "/tmp/ssdd/links"

def test_all_blobs_are_linked():
    """Test if all blobs are linked when instantiating a Blob Service."""

    if not os.path.exists(USED_BLOBS_DIRECTORY) or not os.path.exists(USED_LINKS_DIRECTORY):
        pytest.skip("Directories do not exist")

    blobs = os.listdir(USED_BLOBS_DIRECTORY)
    links = os.listdir(USED_LINKS_DIRECTORY)

    # FIXME: files of directories are in same order?
    assert blobs == links


def test_all_links_are_valid():
    """Test if all blobs are valid, i.e, they have not negative number of links.
    There should be no blobs with -1 links."""

    if not os.path.exists(USED_LINKS_DIRECTORY):
        pytest.skip("Directory does not exist")

    links = os.listdir(USED_LINKS_DIRECTORY)

    for link in links:
        with open(os.path.join(USED_LINKS_DIRECTORY, link), "r") as f:
            assert int(f.read()) >= 0


def test_blobs_ids_are_valid():
    """Test if all blobs ids are valid, i.e, they are the sha256 hash of their contents."""

    read_size = 1024

    if not os.path.exists(USED_BLOBS_DIRECTORY):
        pytest.skip("Directory does not exist")

    blobs = os.listdir(USED_BLOBS_DIRECTORY)

    for blob_id in blobs:
        sha256 = hashlib.sha256()
        with open(os.path.join(USED_BLOBS_DIRECTORY, blob_id), "rb") as f:
            while data := f.read(read_size):
                sha256.update(data)

        assert blob_id == sha256.hexdigest()
