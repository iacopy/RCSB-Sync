"""
Test of download functions.
"""

# Standard Library
import hashlib
import os

# 3rd party
import pytest

# My stuff
import download

HUMAN_INSULIN = "3i40"
HUMAN_INSULIN_SIZE = 64476
HUMAN_INSULIN_MD5 = "edfe5ed81234b32e8ceb7a566129d32b"
HUMAN_INSULIN_SIZE_COMPRESSED = 13828
HUMAN_INSULIN_SIZE_COMPRESSED_MD5 = "1232eb3be7653a90f28241bf02f9605e"
# AlphaFoldDB
# https://alphafold.ebi.ac.uk/files/AF-P01308-F1-model_v3.cif
# https://alphafold.ebi.ac.uk/files/AF-P01308-F1-model_v4.pdb
HUMAN_INSULIN_ALPHAFOLD = "AF_AFP01308F1"
HUMAN_INSULIN_ALPHAFOLD_SIZE = 72575


def datafile(filename: str) -> str:
    """
    Get the path to a test file.
    """
    return os.path.join(os.path.dirname(__file__), "data", filename)


def calculate_md5(file_path: str) -> str:
    """
    Calculate the md5 of a file given its path.
    """
    with open(file_path, "rb") as file_pointer:
        content = file_pointer.read()
    return hashlib.md5(content).hexdigest()


def check_md5(file_path: str, md5: str) -> bool:
    """
    Check that the md5 of a file is the expected one.
    Raises an AssertionError if the md5 is not the expected one.

    Args:
        file_path: Path to the file.
        md5: Expected md5sum.
    """
    assert calculate_md5(file_path) == md5


@pytest.mark.webtest
def test_download_pdb_404(tmp_path):
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
    res = download.download_pdb("0000", datadir, compressed=True)
    assert res == download.PDBDownloadResult(
        pdb_id="0000",
        pdb_url="https://files.rcsb.org/download/0000.pdb.gz",
        pdb_title="",
        local_path=str(datadir / "0000.pdb.gz"),
        status_code=404,
    )
    # Check that the downloaded file is empty.
    assert os.path.getsize(res.local_path) == 0
    # Check that the 404.txt file is updated.
    with open(txt404, encoding="ascii") as file_pointer:
        assert file_pointer.read() == "fake\n0000\n"


@pytest.mark.webtest
def test_download_real_pdb():
    """
    Test the download_pdb function.
    """
    pdb_id = HUMAN_INSULIN
    res = download.download_pdb(pdb_id, directory=".", compressed=False)
    assert res == download.PDBDownloadResult(
        pdb_id=pdb_id,
        pdb_url=f"https://files.rcsb.org/download/{pdb_id}.pdb",
        pdb_title="HUMAN INSULIN",
        local_path=f"./{pdb_id}.pdb",
        status_code=200,
    )
    assert os.path.exists(res.local_path)
    assert (
        os.path.getsize(res.local_path) == HUMAN_INSULIN_SIZE
    ), "Wrong size for the downloaded file (?!)"
    # Check the md5sum of the file.
    check_md5(res.local_path, HUMAN_INSULIN_MD5)
    os.remove(res.local_path)


@pytest.mark.webtest
def test_download_real_pdb_title_section_only():
    """
    Test the download_pdb function with title_section_only=True.
    """
    pdb_id = HUMAN_INSULIN
    res = download.download_pdb(
        pdb_id, directory=".", compressed=False, title_section_only=True
    )
    assert res == download.PDBDownloadResult(
        pdb_id=pdb_id,
        pdb_url=f"https://files.rcsb.org/download/{pdb_id}.pdb",
        pdb_title="HUMAN INSULIN",
        local_path=f"./{pdb_id}.pdb",
        status_code=200,
    )
    assert os.path.exists(res.local_path)
    assert (
        os.path.getsize(res.local_path) < HUMAN_INSULIN_SIZE
    ), "Wrong size for the downloaded file (?!)"
    with open(res.local_path, "r", encoding="ascii") as file_pointer:
        content = file_pointer.read()
    # No atoms should be present in the file.
    # Get all the first words of each line.
    first_words = {line.split()[0] for line in content.splitlines()}
    assert first_words.issubset(
        {
            "HEADER",
            "OBSLTE",
            "TITLE",
            "SPLIT",
            "CAVEAT",
            "COMPND",
            "SOURCE",
            "KEYWDS",
            "EXPDTA",
            "AUTHOR",
            "REVDAT",
            "SPRSDE",
            "JRNL",
            "REMARK",
            "DBREF",
        }
    ), f"Unexpected line types in the downloaded file: {first_words}"
    check_md5(res.local_path, "73d9ac72e546007b266163db560743f0")
    os.remove(res.local_path)


@pytest.mark.webtest
def test_download_real_alphafold_pdb():
    """
    Test the download_pdb function.
    """
    pdb_id = HUMAN_INSULIN_ALPHAFOLD
    res = download.download_pdb(pdb_id, directory=".", compressed=False)
    assert res == download.PDBDownloadResult(
        pdb_id=pdb_id,
        pdb_url="https://alphafold.ebi.ac.uk/files/AF-P01308-F1-model_v4.pdb",
        pdb_title="ALPHAFOLD MONOMER V2.0 PREDICTION FOR INSULIN (P01308)",
        local_path="./AF-P01308-F1-model_v4.pdb",
        status_code=200,
    )
    dest = res.local_path
    assert os.path.exists(dest)
    assert (
        os.path.getsize(dest) == HUMAN_INSULIN_ALPHAFOLD_SIZE
    ), "Wrong size for the downloaded file (?!)"

    reference_file = datafile("test_AF-P01308-F1-model_v4.pdb")
    with open(dest, "r", encoding="ascii") as file_pointer:
        content = file_pointer.read()
    with open(reference_file, "r", encoding="ascii") as file_pointer:
        reference = file_pointer.read()
    assert "TITLE     ALPHAFOLD MONOMER V2.0 PREDICTION FOR INSULIN (P01308)" in content
    assert content == reference, "Wrong content for the downloaded file (?!)"

    os.remove(dest)


@pytest.mark.webtest
def test_download_real_pdb_compressed():
    """
    Test the download_pdb function with compressed files.
    """
    pdb_id = HUMAN_INSULIN
    res = download.download_pdb(pdb_id, directory=".", compressed=True)
    assert res == download.PDBDownloadResult(
        pdb_id=pdb_id,
        pdb_url=f"https://files.rcsb.org/download/{pdb_id}.pdb.gz",
        pdb_title="",
        local_path=f"./{pdb_id}.pdb.gz",
        status_code=200,
    )
    dest = res.local_path
    assert os.path.exists(dest)
    assert (
        os.path.getsize(dest) == HUMAN_INSULIN_SIZE_COMPRESSED
    ), "Wrong size for the downloaded compressed file (?!)"
    assert (
        HUMAN_INSULIN_SIZE_COMPRESSED < HUMAN_INSULIN_SIZE
    ), "Ops.. your fault? Compressed size bigger than uncompressed"
    assert dest.endswith(".gz")
    # Check the md5sum of the file.
    check_md5(dest, HUMAN_INSULIN_SIZE_COMPRESSED_MD5)
    os.remove(dest)


@pytest.mark.webtest
def test_function_download__404(tmp_path):
    """
    Add coverage for the download function when the pdb is not found.
    This PDB ids are real, but only one has a PDB file available for download.
    """
    datadir = tmp_path / "data"
    datadir.mkdir()
    ids = ["6BP8", "7PKR", "7PKY"]
    download.download(ids, datadir, compressed=False)

    # Test that only 6BP8.pdb is found.
    assert os.path.getsize(datadir / "6BP8.pdb") > 0
    assert os.path.getsize(datadir / "7PKR.pdb") == 0
    assert os.path.getsize(datadir / "7PKY.pdb") == 0
