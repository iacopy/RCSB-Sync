"""
Integration tests.
"""

# Standard Library
import os
import shutil
from unittest.mock import patch

# 3rd party
import pytest

# My stuff
import project

# Mark all tests in this module as integration tests.
pytestmark = pytest.mark.integration


def check_nodata(project_dir):
    """
    Check that the project directory contains no data.
    """
    assert os.path.isdir(project_dir)
    # check that the data directory does not exist
    assert not os.path.isdir(os.path.join(project_dir, "data"))
    # check the main level: no files, only the queries directory
    assert sorted(os.listdir(project_dir)) == ["queries"]
    # check queries directory contain 2 json files
    queries_dir = os.path.join(project_dir, "queries")
    assert sorted(os.listdir(queries_dir)) == [
        "Rabbitpox virus.json",
        "Radianthus crispus.json",
    ]


def check_data__datav1(project_dir, allow_cache=False):
    """
    Check that the project directory contains the data, in the old layout.
    """
    assert os.path.isdir(project_dir)
    # check that the data directory exists
    assert os.path.isdir(os.path.join(project_dir, "data"))
    # check that the data directory contains the downloaded files
    assert set(os.listdir(os.path.join(project_dir, "data"))) == {
        "2FFK.pdb.gz",
        "2FIN.pdb.gz",
        "1YZW.pdb.gz",
        "6DEJ.pdb.gz",
        "6Y1G.pdb.gz",
    }

    if not allow_cache:
        # check the main level: no files, only the queries directory
        assert sorted(os.listdir(project_dir)) == ["data", "queries"]
    # check queries directory contain 2 json files
    queries_dir = os.path.join(project_dir, "queries")
    assert sorted(os.listdir(queries_dir)) == [
        "Rabbitpox virus.json",
        "Radianthus crispus.json",
    ]


def check_data__new_layout(project_dir, allow_cache=False):
    """
    Check that the project directory contains the data, in the new layout.
    """
    assert os.path.isdir(project_dir)
    # check that the data directory exists
    assert os.path.isdir(os.path.join(project_dir, "data"))

    if not allow_cache:
        # check the main level: no files, only the queries directory
        assert sorted(os.listdir(project_dir)) == ["data", "queries"]

    # check queries directory contain 2 json files
    queries_dir = os.path.join(project_dir, "queries")
    assert sorted(os.listdir(queries_dir)) == [
        "Rabbitpox virus.json",
        "Radianthus crispus.json",
    ]

    # Check that the data directory contains the downloaded files
    # The data directory should contain 2 directories ("Rabbitpox virus" and "Radianthus crispus")
    assert set(os.listdir(os.path.join(project_dir, "data"))) == {
        "Rabbitpox virus",
        "Radianthus crispus",
    }
    # check the data subdirectories
    assert set(os.listdir(os.path.join(project_dir, "data", "Rabbitpox virus"))) == {
        "2FFK.pdb.gz",
        "2FIN.pdb.gz",
    }
    assert set(os.listdir(os.path.join(project_dir, "data", "Radianthus crispus"))) == {
        "1YZW.pdb.gz",
        "6DEJ.pdb.gz",
        "6Y1G.pdb.gz",
    }


def clean_cache_files(project_dir):
    """
    Clean the cache files.
    """
    # remove '.DS_Store' file if present
    if os.path.isfile(os.path.join(project_dir, ".DS_Store")):
        os.remove(os.path.join(project_dir, ".DS_Store"))
    # remove the cache '_ids_<date>.txt' files
    for file in os.listdir(project_dir):
        if file.startswith("_ids_"):
            os.remove(os.path.join(project_dir, file))


@pytest.fixture
def project_w_data_cleanup():
    """
    Fixture to clean up the project directory after the test.
    """
    project_dir = os.path.join(os.path.dirname(__file__), "test-project-w-data")
    # pre-checks
    check_data__datav1(project_dir)

    yield project_dir

    # cleanup of cache files (but not the downloaded files)
    clean_cache_files(project_dir)


@pytest.fixture
def project_nodata_cleanup():
    """
    Fixture to clean up the data directory after the test.
    """
    project_dir = os.path.join(os.path.dirname(__file__), "test-project-nodata")
    # pre-checks
    check_nodata(project_dir)

    yield project_dir

    # cleanup of downloaded files and cache
    clean_cache_files(project_dir)
    # remove the data directory
    data_dir = os.path.join(project_dir, "data")
    # Completely remove the data directory, even if it is not empty.
    if os.path.isdir(data_dir):
        shutil.rmtree(data_dir)


def test_project_download__datav1(project_nodata_cleanup):
    """
    Test that the project downloads the files in the old layout.
    """
    project_dir = os.path.join(os.path.dirname(__file__), "test-project-nodata")

    # pre-checks
    check_nodata(project_dir)

    project.main(project_dir, yes=True)

    # check that the data directory exists
    check_data__datav1(project_dir, allow_cache=True)
    data_stat_1 = os.stat(os.path.join(project_dir, "data"))

    # Relaunch the project to check that the files are not downloaded again
    # NB: this should be a separate test.
    project.main(project_dir, yes=True)

    check_data__datav1(project_dir, allow_cache=True)
    data_stat_2 = os.stat(os.path.join(project_dir, "data"))
    assert data_stat_1 == data_stat_2

    # cleanup of downloaded files and cache (done by the fixture)


@pytest.mark.xfail(
    reason="This test will pass with the data directory layout v2", strict=True
)
def test_project_download(project_nodata_cleanup):
    """
    Start from an existing directory with real queries.
    """
    project_dir = project_nodata_cleanup

    # launch main, bypassing the user input (yes to download)
    project.main(project_dir, yes=True)

    # post-checks
    # The data directory should contain 2 directories ("Rabbitpox virus" and "Radianthus crispus")
    data_dir = os.path.join(project_dir, "data")
    assert sorted(os.listdir(data_dir)) == ["Rabbitpox virus", "Radianthus crispus"]
    # The "Rabbitpox virus" directory should contain 2 files.
    assert sorted(os.listdir(os.path.join(data_dir, "Rabbitpox virus"))) == [
        "2FFK.pdb.gz",
        "2FIN.pdb.gz",
    ]

    # The "Radianthus crispus" directory should contain 3 files.
    assert sorted(os.listdir(os.path.join(data_dir, "Radianthus crispus"))) == [
        "1YZW.pdb.gz",
        "6DEJ.pdb.gz",
        "6Y1G.pdb.gz",
    ]

    # cleanup of downloaded files and cache (done by the fixture)


@pytest.mark.xfail(
    reason="This test will pass with the data directory layout v2", strict=True
)
def test_project_no_updates(project_w_data_cleanup):
    """
    The database is already synced, no need to update.
    If we run the program again, it should not download anything, and the data directory should not change.
    """
    project_dir = os.path.join(os.path.dirname(__file__), "test-project-w-data")
    # pre-checks
    check_data__new_layout(project_dir)

    # mock the sync (download) method to avoid actually downloading anything
    # (to be removed in the integration test: useful now because the actual implementation
    # would download the data again, since the current directory layout searches for the dowloaded data
    # in the wrong place)
    with patch("project.Project.sync") as mock_sync:
        # launch main, bypassing the user input (yes to download)
        project.main(project_dir, yes=True)

    # check that the sync function was *not* called (no download)
    # (to be removed when the actual implementation is fixed)
    mock_sync.assert_not_called()

    # post-checks
    check_data__new_layout(project_dir)


@patch("builtins.input", lambda *args: "n")
def test_main_outdated__but_user_dont_sync(project_nodata_cleanup):
    """
    When the first time the project check for updates, all the remote ids are considered to be downloaded.
    Test that the user can choose not to download anything.
    """
    project_dir = os.path.join(os.path.dirname(__file__), "test-project-nodata")

    with patch("project.Project.sync") as mock_sync:
        # launch main, ask the user input (no to download)
        project.main(project_dir)

    # The sync() method should not be called (because the user answered "n" to the question).
    mock_sync.assert_not_called()


@patch("builtins.input", lambda *args: "y")
def test_main_outdated__and_user_sync(project_nodata_cleanup):
    """
    When the first time the project check for updates, all the remote ids are considered to be downloaded.
    Test that the user can choose not to download anything.
    """
    project_dir = os.path.join(os.path.dirname(__file__), "test-project-nodata")

    with patch("project.Project.sync") as mock_sync:
        # launch main, ask the user input (yes to download)
        project.main(project_dir)

    # The sync() method should be called (because the user answered "y" to the question).
    mock_sync.assert_called_once()
