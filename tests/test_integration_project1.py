"""
Integration tests.
"""

# Standard Library
import os
from unittest.mock import patch

# 3rd party
import pytest
import testutils

# My stuff
import project1

# Mark all tests in this module as integration tests.
pytestmark = pytest.mark.integration


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
    # pylint: disable=duplicate-code
    if not allow_cache:
        # check the main level: no files, only the queries directory
        assert sorted(os.listdir(project_dir)) == ["data", "queries"]
    # check queries directory contain 2 json files
    queries_dir = os.path.join(project_dir, "queries")
    assert sorted(os.listdir(queries_dir)) == [
        "Rabbitpox virus.json",
        "Radianthus crispus.json",
    ]


@pytest.fixture
def project_w_datav1_cleanup():
    """
    Fixture to clean up the project directory after the test.
    """
    project_dir = os.path.join(os.path.dirname(__file__), "test-project-w-data")
    # pre-checks
    check_data__datav1(project_dir)

    yield project_dir

    # cleanup of cache files (but not the downloaded files)
    testutils.clean_cache_files(project_dir)


def test_project_download__datav1(project_nodata_cleanup):
    """
    Test that the project downloads the files in the old layout.
    """
    project_dir = os.path.join(os.path.dirname(__file__), "test-project-nodata")

    # pre-checks
    testutils.check_nodata(project_dir)

    project1.main(project_dir, yes=True)

    # check that the data directory exists
    check_data__datav1(project_dir, allow_cache=True)
    data_stat_1 = os.stat(os.path.join(project_dir, "data"))

    # Relaunch the project to check that the files are not downloaded again
    # NB: this should be a separate test.
    project1.main(project_dir, yes=True)

    check_data__datav1(project_dir, allow_cache=True)
    data_stat_2 = os.stat(os.path.join(project_dir, "data"))
    assert data_stat_1 == data_stat_2

    # cleanup of downloaded files and cache (done by the fixture)


@patch("builtins.input", lambda *args: "n")
def test_main_outdated__but_user_dont_sync(project_nodata_cleanup):
    """
    When the first time the project check for updates, all the remote ids are considered to be downloaded.
    Test that the user can choose not to download anything.
    """
    project_dir = os.path.join(os.path.dirname(__file__), "test-project-nodata")

    with patch("project1.Project.sync") as mock_sync:
        # launch main, ask the user input (no to download)
        project1.main(project_dir)

    # The sync() method should not be called (because the user answered "n" to the question).
    mock_sync.assert_not_called()


@patch("builtins.input", lambda *args: "y")
def test_main_outdated__and_user_sync(project_nodata_cleanup):
    """
    When the first time the project check for updates, all the remote ids are considered to be downloaded.
    Test that the user can choose not to download anything.
    """
    project_dir = os.path.join(os.path.dirname(__file__), "test-project-nodata")

    with patch("project1.Project.sync") as mock_sync:
        # launch main, ask the user input (yes to download)
        project1.main(project_dir)

    # The sync() method should be called (because the user answered "y" to the question).
    mock_sync.assert_called_once()
