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


def check_files(directory, expected):
    """
    Check files in directory

    Cleanup .DS_Store before checking
    """
    if os.path.isfile(os.path.join(directory, ".DS_Store")):
        os.remove(os.path.join(directory, ".DS_Store"))
    assert set(os.listdir(directory)) == expected


def check_data(project_dir, allow_cache=False):
    """
    Check that the project directory contains the data, in the new layout.
    """
    assert os.path.isdir(project_dir)
    # check that the data directory exists
    assert os.path.isdir(os.path.join(project_dir, "data"))
    project_dirname = os.path.basename(project_dir)

    if not allow_cache:
        # check the main level files
        check_files(
            project_dir,
            {
                "data",
                "db_summary.csv",
                "README.md",
                "queries",
                f"{project_dirname}__files.csv",
            },
        )

    # check queries directory contain 2 json files
    queries_dir = os.path.join(project_dir, "queries")
    check_files(
        queries_dir,
        {
            "Rabbitpox_virus.json",
            "Radianthus_crispus.json",
        },
    )

    # Check that the data directory contains the downloaded files
    # The data directory should contain 2 directories ("Rabbitpox_virus" and "Radianthus_crispus")

    # Rmove .DS_Store file if present
    check_files(
        os.path.join(project_dir, "data"),
        {
            "Rabbitpox_virus",
            "Rabbitpox_virus.ids",
            "Rabbitpox_virus.sh",
            "Rabbitpox_virus__files.csv",
            "Radianthus_crispus",
            "Radianthus_crispus.ids",
            "Radianthus_crispus.sh",
            "Radianthus_crispus__files.csv",
        },
    )
    # check the data subdirectories
    check_files(
        os.path.join(project_dir, "data", "Rabbitpox_virus"),
        {
            "2FFK.pdb.gz",
            "2FIN.pdb.gz",
        },
    )
    check_files(
        os.path.join(project_dir, "data", "Radianthus_crispus"),
        {
            "1YZW.pdb.gz",
            "6DEJ.pdb.gz",
            "6Y1G.pdb.gz",
        },
    )


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
    check_files(
        data_dir,
        {
            "Rabbitpox_virus",
            "Rabbitpox_virus.ids",
            "Rabbitpox_virus.sh",
            "Rabbitpox_virus__files.csv",
            "Radianthus_crispus",
            "Radianthus_crispus.ids",
            "Radianthus_crispus.sh",
            "Radianthus_crispus__files.csv",
        },
    )
    # The "Rabbitpox_virus" directory should contain 2 files.
    check_files(
        os.path.join(data_dir, "Rabbitpox_virus"),
        {
            "2FFK.pdb.gz",
            "2FIN.pdb.gz",
        },
    )

    # The "Radianthus_crispus" directory should contain 3 files.
    check_files(
        os.path.join(data_dir, "Radianthus_crispus"),
        {
            "1YZW.pdb.gz",
            "6DEJ.pdb.gz",
            "6Y1G.pdb.gz",
        },
    )

    # Check that ids are stored in .ids files in the data directory
    assert os.path.isfile(os.path.join(data_dir, "Rabbitpox_virus.ids"))
    assert os.path.isfile(os.path.join(data_dir, "Radianthus_crispus.ids"))
    # Check that the ids are correct
    with open(
        os.path.join(data_dir, "Rabbitpox_virus.ids"), encoding="ascii"
    ) as file_pointer:
        assert file_pointer.read().splitlines() == ["2FFK", "2FIN"]
    with open(
        os.path.join(data_dir, "Radianthus_crispus.ids"), encoding="ascii"
    ) as file_pointer:
        assert file_pointer.read().splitlines() == ["1YZW", "6DEJ", "6Y1G"]

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
    check_files(
        data_dir,
        {
            "Rabbitpox_virus",
            "Rabbitpox_virus.ids",
            "Rabbitpox_virus.sh",
            "Rabbitpox_virus__files.csv",
        },
    )
    # The "Rabbitpox_virus" directory should contain 2 files.
    check_files(
        os.path.join(data_dir, "Rabbitpox_virus"),
        {
            "2FFK.pdb",
            "2FIN.pdb",
        },
    )

    # Check that ids are stored in txt files in the data directory
    assert os.path.isfile(os.path.join(data_dir, "Rabbitpox_virus.ids"))
    # Check that the ids are correct
    with open(
        os.path.join(data_dir, "Rabbitpox_virus.ids"), encoding="ascii"
    ) as file_pointer:
        assert file_pointer.read().splitlines() == ["2FFK", "2FIN"]

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


def test_project_noop(project_nodata_cleanup):
    """
    Test the option --noop.

    There are files to download (not tested here),
    but the --noop option should prevent the download.
    """
    project_dir = project_nodata_cleanup

    # launch main with --noop
    with patch("project.Project.do_sync") as mock_sync:
        project.main(project_dir, noop=True)

    # check that the sync function was *not* called (no download)
    mock_sync.assert_not_called()

    # Check that the data subdirectories are empty
    data_dir = os.path.join(project_dir, "data")
    check_files(
        data_dir,
        {
            "Rabbitpox_virus",
            "Rabbitpox_virus.ids",
            "Rabbitpox_virus.sh",
            "Rabbitpox_virus__files.csv",
            "Radianthus_crispus",
            "Radianthus_crispus.ids",
            "Radianthus_crispus.sh",
            "Radianthus_crispus__files.csv",
        },
    )
    check_files(os.path.join(data_dir, "Rabbitpox_virus"), set())
    check_files(os.path.join(data_dir, "Radianthus_crispus"), set())

    # cleanup of downloaded files and cache (done by the fixture)


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
