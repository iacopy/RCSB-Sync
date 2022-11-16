"""
Integration tests for project.
"""
# Standard Library
import os
from unittest.mock import patch

# 3rd party
import pytest
import testutils

# My stuff
import project

# Mark all tests in this module as integration tests.
pytestmark = pytest.mark.integration


def check_data(project_dir, allow_cache=False):
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
        "Rabbitpox_virus.json",
        "Radianthus_crispus.json",
    ]

    # Check that the data directory contains the downloaded files
    # The data directory should contain 2 directories ("Rabbitpox_virus" and "Radianthus_crispus")
    assert set(os.listdir(os.path.join(project_dir, "data"))) == {
        "Rabbitpox_virus",
        "Radianthus_crispus",
    }
    # check the data subdirectories
    assert set(os.listdir(os.path.join(project_dir, "data", "Rabbitpox_virus"))) == {
        "2FFK.pdb.gz",
        "2FIN.pdb.gz",
    }
    assert set(os.listdir(os.path.join(project_dir, "data", "Radianthus_crispus"))) == {
        "1YZW.pdb.gz",
        "6DEJ.pdb.gz",
        "6Y1G.pdb.gz",
    }


@pytest.fixture
def project_w_data_cleanup():
    """
    Fixture to clean up the project directory after the test.
    """
    project_dir = os.path.join(os.path.dirname(__file__), "test-prj-w-data")
    # pre-checks
    check_data(project_dir)

    yield project_dir

    # cleanup of cache files (but not the downloaded files)
    testutils.clean_cache_files(project_dir)


@pytest.mark.webtest
def test_project_download(project_nodata_cleanup):
    """
    Start from an existing directory with real queries.
    """
    project_dir = project_nodata_cleanup

    # launch main, bypassing the user input (yes to download)
    project.main(project_dir, yes=True, compressed=True)

    # post-checks
    # The data directory should contain 2 directories ("Rabbitpox_virus" and "Radianthus_crispus")
    data_dir = os.path.join(project_dir, "data")
    assert sorted(os.listdir(data_dir)) == ["Rabbitpox_virus", "Radianthus_crispus"]
    # The "Rabbitpox_virus" directory should contain 2 files.
    assert sorted(os.listdir(os.path.join(data_dir, "Rabbitpox_virus"))) == [
        "2FFK.pdb.gz",
        "2FIN.pdb.gz",
    ]

    # The "Radianthus_crispus" directory should contain 3 files.
    assert sorted(os.listdir(os.path.join(data_dir, "Radianthus_crispus"))) == [
        "1YZW.pdb.gz",
        "6DEJ.pdb.gz",
        "6Y1G.pdb.gz",
    ]

    # cleanup of downloaded files and cache (done by the fixture)


@pytest.mark.webtest
def test_project_download_uncompressed(project_rabbitpox_nodata_cleanup):
    """
    Start from an existing directory with real queries.
    """
    project_dir = project_rabbitpox_nodata_cleanup

    # launch main, bypassing the user input (yes to download)
    project.main(project_dir, yes=True, compressed=False)

    # post-checks
    # The data directory should contain 1 directory ("Rabbitpox_virus")
    data_dir = os.path.join(project_dir, "data")
    assert sorted(os.listdir(data_dir)) == ["Rabbitpox_virus"]
    # The "Rabbitpox_virus" directory should contain 2 files.
    assert sorted(os.listdir(os.path.join(data_dir, "Rabbitpox_virus"))) == [
        "2FFK.pdb",
        "2FIN.pdb",
    ]

    # cleanup of downloaded files and cache (done by the fixture)


@pytest.mark.webtest
def test_project_no_updates(project_w_data_cleanup):
    """
    The database is already synced, no need to update.
    If we run the program again, it should not download anything, and the data directory should not change.
    """
    project_dir = os.path.join(os.path.dirname(__file__), "test-prj-w-data")
    # pre-checks
    check_data(project_dir)

    # mock the sync (download) method to avoid actually downloading anything
    # (to be removed in the integration test: useful now because the actual implementation
    # would download the data again, since the current directory layout searches for the dowloaded data
    # in the wrong place)
    with patch("project.Project.do_sync") as mock_sync:
        # launch main, bypassing the user input (yes to download)
        project.main(project_dir, yes=True)

    # check that the sync function was *not* called (no download)
    # (to be removed when the actual implementation is fixed)
    mock_sync.assert_not_called()

    # post-checks
    check_data(project_dir)


# User input

@pytest.mark.webtest
@patch("builtins.input", lambda *args: "n")
def test_main2_outdated__but_user_dont_sync(project_nodata_cleanup):
    """
    When the first time the project check for updates, all the remote ids are considered to be downloaded.
    Test that the user can choose not to download anything.
    """
    project_dir = os.path.join(os.path.dirname(__file__), "test-prj-nodata")

    with patch("project.Project.do_sync") as mock_sync:
        # launch main, ask the user input (no to download)
        project.main(project_dir)

    # The sync() method should not be called (because the user answered "n" to the question).
    mock_sync.assert_not_called()


@pytest.mark.webtest
@patch("builtins.input", lambda *args: "y")
def test_main2_outdated__and_user_sync(project_nodata_cleanup):
    """
    When the first time the project check for updates, all the remote ids are considered to be downloaded.
    Test that the user can choose not to download anything.
    """
    project_dir = os.path.join(os.path.dirname(__file__), "test-prj-nodata")

    with patch("project.Project.do_sync") as mock_sync:
        # launch main, ask the user input (yes to download)
        project.main(project_dir)

    # The sync() method should be called (because the user answered "y" to the question).
    mock_sync.assert_called_once()
