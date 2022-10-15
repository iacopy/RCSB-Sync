"""
Unit tests for the project module.
"""
# Standard Library
import os

# 3rd party
import pytest

# My stuff
from project import Project
from rcsbids import SEARCH_ENDPOINT_URI


def test_project_non_existing_directory():
    """Test the creation of a project raises an exception if the directory does not exist."""
    # Create a project in a non-existing directory.
    with pytest.raises(FileNotFoundError):
        Project("non-existing-directory")


def test_updiff_the_first_time(empty_project, remote_server):
    """
    Test that the first time the project check for updates, all the remote ids are considered to be downloaded.
    """
    tbd_ids, removed_ids = empty_project.updiff()
    assert set(tbd_ids) == {"hs01", "hs02", "rn01", "rn02"}
    assert removed_ids == []


def test_second_updiff_same_results(empty_project, remote_server):
    """
    Test two subsequent updiffs with no download.
    The second updiff (which loads ids from the local cache) should return the same ids as the first one.
    The second updiff should not call the remote server.

    If the test fails, it could be indicating that the local cache is not working properly.
    """
    # First updiff.
    tbd_ids, removed_ids = empty_project.updiff()
    assert set(tbd_ids) == {"hs01", "hs02", "rn01", "rn02"}
    assert removed_ids == []

    # The requests.get() method should be called two times, since there are two queries.
    assert len(remote_server.calls) == 2

    # Second updiff.
    tbd_ids, removed_ids = empty_project.updiff()
    assert set(tbd_ids) == {"hs01", "hs02", "rn01", "rn02"}
    assert removed_ids == []

    # The second updiff should not call requests.get() (because the ids are loaded from the local cache).
    assert len(remote_server.calls) == 2


def test_removed_handling(project_with_files, mocked_responses):
    """
    Test that the remote-removed ids are handled properly.
    """
    # NB: this code should be refactored, since is a duplicate of a part of remote_server fixture.
    mocked_responses.get(
        url=f"{SEARCH_ENDPOINT_URI}",
        body='{"result_set": [{"identifier": "hs01"}, {"identifier": "hs02"}]}',
        status=200,
        content_type="application/json",
    )
    # The remote server returns a different set of ids (rn02 is removed).
    mocked_responses.get(
        url=f"{SEARCH_ENDPOINT_URI}",
        body='{"result_set": [{"identifier": "rn01"}]}',
        status=200,
        content_type="application/json",
    )

    updiff_result = project_with_files.updiff()
    assert updiff_result.tbd_ids == []
    assert updiff_result.removed_ids == ["rn02"]

    # The requests.get() method should be called two times, since there are two queries.
    assert len(mocked_responses.calls) == 2

    assert sorted(os.listdir(project_with_files.data_dir)) == [
        "hs01.pdb.gz",
        "hs02.pdb.gz",
        "rn01.pdb.gz",
        "rn02.pdb.gz",
    ]
    project_with_files.handle_removed(updiff_result)
    assert sorted(os.listdir(project_with_files.data_dir)) == [
        "hs01.pdb.gz",
        "hs02.pdb.gz",
        "rn01.pdb.gz",
        "rn02.pdb.gz.obsolete",
    ]
