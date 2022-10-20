"""
Test of download functions.
"""

# Standard Library
import os

# 3rd party
import pytest

# My stuff
import download

HUMAN_INSULIN = "3i40"
HUMAN_INSULIN_SIZE = 64476
HUMAN_INSULIN_SIZE_COMPRESSED = 13849


@pytest.mark.webtest
def test_download_404(tmp_path):
    """Test that if a pdb is not found, no exception is raised, but
    the downloaded file is empty. Then, check that the 404.txt list
    is updated.
    """
    datadir = tmp_path / "data"
    datadir.mkdir()
    txt404 = datadir / "404.txt"
    # fill the 404.txt file with a fake id
    txt404.write_text("fake\n", encoding="ascii")

    # Download a pdb that does not exist.
    dest = download.download_pdb("0000", datadir)
    # Check that the downloaded file is empty.
    assert os.path.getsize(dest) == 0
    # Check that the 404.txt file is updated.
    with open(txt404, encoding="ascii") as file_pointer:
        assert file_pointer.read() == "fake\n0000\n"


@pytest.mark.webtest
def test_download_real_pdb():
    """
    Test the download_pdb function.
    """
    pdb_id = HUMAN_INSULIN
    dest = download.download_pdb(pdb_id, directory=".", compressed=False)
    assert os.path.exists(dest)
    assert (
        os.path.getsize(dest) == HUMAN_INSULIN_SIZE
    ), "Wrong size for the downloaded file (?!)"
    os.remove(dest)


@pytest.mark.webtest
def test_download_real_pdb_compressed():
    """
    Test the download_pdb function with compressed files.
    """
    pdb_id = HUMAN_INSULIN
    dest = download.download_pdb(pdb_id, directory=".", compressed=True)
    assert os.path.exists(dest)
    assert (
        os.path.getsize(dest) == HUMAN_INSULIN_SIZE_COMPRESSED
    ), "Wrong size for the downloaded compressed file (?!)"
    assert (
        HUMAN_INSULIN_SIZE_COMPRESSED < HUMAN_INSULIN_SIZE
    ), "Ops.. your fault? Compressed size bigger than uncompressed"
    assert dest.endswith(".gz")
    os.remove(dest)
