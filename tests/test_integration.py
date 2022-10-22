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


@pytest.fixture
def project_dir_cleanup():
    """
    Fixture to clean up the data directory.
    """
    project_dir = os.path.join(os.path.dirname(__file__), "test-project-nodata")
    # pre-checks
    assert os.path.isdir(project_dir)
    # check the main level: no files, only the queries directory
    assert sorted(os.listdir(project_dir)) == ["queries"]
    # check queries directory contain 2 json files
    queries_dir = os.path.join(project_dir, "queries")
    assert sorted(os.listdir(queries_dir)) == [
        "Rabbitpox virus.json",
        "Radianthus crispus.json",
    ]

    yield project_dir

    # remove '.DS_Store' file if present
    if os.path.isfile(os.path.join(project_dir, ".DS_Store")):
        os.remove(os.path.join(project_dir, ".DS_Store"))
    # remove the cache '_ids_<date>.txt' files
    for file in os.listdir(project_dir):
        if file.startswith("_ids_"):
            os.remove(os.path.join(project_dir, file))
    data_dir = os.path.join(project_dir, "data")
    # Completely remove the data directory, even if it is not empty.
    if os.path.isdir(data_dir):
        shutil.rmtree(data_dir)


@pytest.mark.xfail(
    reason="This test will pass with the data directory layout v2", strict=True
)
def test_project_download(project_dir_cleanup):
    """
    Start from an existing directory with real queries.
    """
    project_dir = project_dir_cleanup

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


@pytest.mark.xfail(
    reason="This test will pass with the data directory layout v2", strict=True
)
def test_project_no_updates():
    """
    The database is already synced, no need to update.
    If we run the program again, it should not download anything, and the data directory should not change.
    """

    def checks(project_dir):
        assert os.path.isdir(project_dir)
        # check the main level: no files, only the queries directory (skip the cache file)
        assert [
            dir_ for dir_ in sorted(os.listdir(project_dir)) if not dir_.startswith("_")
        ] == ["data", "queries"]
        # check queries directory contain 2 json files
        queries_dir = os.path.join(project_dir, "queries")
        assert sorted(os.listdir(queries_dir)) == [
            "Rabbitpox virus.json",
            "Radianthus crispus.json",
        ]

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

    project_dir = os.path.join(os.path.dirname(__file__), "test-project-w-data")
    # pre-checks
    checks(project_dir)

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
    checks(project_dir)
