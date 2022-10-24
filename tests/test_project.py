"""
Unit tests for the project module.
"""
# Standard Library
import os

# 3rd party
import pytest

# My stuff
from project import Project


def test_project_non_existing_directory():
    """Test the creation of a project raises an exception if the directory does not exist."""
    # Create a project in a non-existing directory.
    with pytest.raises(FileNotFoundError):
        Project("non-existing-directory")


def test_updiff_the_first_time__datav1(new_project, remote_server):
    """
    Test that the first time the project check for updates, all the remote ids are considered to be downloaded.
    """
    tbd_ids, removed_ids = new_project.updiff()
    assert set(tbd_ids) == {"hs01", "hs02", "hs03", "rn01", "rn02"}
    assert removed_ids == []


def test_updiff_resume_rn__datav1(project_with_hs_files__datav1, remote_server):
    """
    Test that resuming a download works properly (Homo sapiens is already downloaded).
    """
    # Check for updates.
    updiff_result = project_with_hs_files__datav1.updiff()
    assert updiff_result.tbd_ids == ["rn01", "rn02"]
    assert updiff_result.removed_ids == []


def test_updiff_resume_hs__datav1(project_with_rn_files__datav1, remote_server):
    """
    Test that resuming a download works properly (Rattus norvegicus is already downloaded).
    """
    # Check for updates.
    updiff_result = project_with_rn_files__datav1.updiff()
    assert updiff_result.tbd_ids == ["hs01", "hs02", "hs03"]
    assert updiff_result.removed_ids == []
    # The requests.get() method should be called two times, since there are two queries.
    assert len(remote_server.calls) == 2


@pytest.mark.xfail(reason="The new data layout (datav2) is not implemented yet.", strict=True)
def test_updiff_the_first_time__datav2(new_project, remote_server):
    """
    Test that the first time the project check for updates, all the remote ids are considered to be downloaded.
    """
    tbd_ids, removed_ids = new_project.updiff()

    assert tbd_ids == {
        "Homo sapiens": ["hs01", "hs02", "hs03"],
        "Rattus norvegicus": ["rn01", "rn02"],
    }
    assert removed_ids == []


@pytest.mark.xfail(reason="The new data layout (datav2) is not implemented yet.", strict=True)
def test_updiff_resume_rn__datav2(project_with_hs_files, remote_server):
    """
    Test that resuming a download works properly (Homo sapiens is already downloaded).
    """
    tbd_ids, removed_ids = project_with_hs_files.updiff()

    assert tbd_ids == {
        "Homo sapiens": [],
        "Rattus norvegicus": ["rn01", "rn02"],
    }
    assert removed_ids == []


@pytest.mark.xfail(reason="The new data layout (datav2) is not implemented yet.", strict=True)
def test_updiff_resume_hs__datav2(project_with_hs_files, remote_server):
    """
    Test that resuming a download works properly (Rattus norvegicus is already downloaded).
    """
    tbd_ids, removed_ids = project_with_hs_files.updiff()

    assert tbd_ids == {
        "Homo sapiens": ["hs01", "hs02", "hs03"],
        "Rattus norvegicus": [],
    }
    assert removed_ids == []


def test_second_updiff_same_results__datav1(new_project, remote_server):
    """
    Test two subsequent updiffs with no download.
    The second updiff (which loads ids from the local cache) should return the same ids as the first one.
    The second updiff should not call the remote server.

    If the test fails, it could be indicating that the local cache is not working properly.
    """
    # First updiff.
    tbd_ids, removed_ids = new_project.updiff()
    assert set(tbd_ids) == {"hs01", "hs02", "hs03", "rn01", "rn02"}
    assert removed_ids == []

    # The requests.get() method should be called two times, since there are two queries.
    assert len(remote_server.calls) == 2

    # Second updiff.
    tbd_ids, removed_ids = new_project.updiff()
    assert set(tbd_ids) == {"hs01", "hs02", "hs03", "rn01", "rn02"}
    assert removed_ids == []

    # The second updiff should not call requests.get() (because the ids are loaded from the local cache).
    assert len(remote_server.calls) == 2


def test_updiff_uptodate__datav1(project_with_files__datav1, remote_server):
    """
    Test that the updiff method returns an empty list of ids if the local data is up-to-date.
    """
    # Check for updates.
    updiff_result = project_with_files__datav1.updiff()
    assert updiff_result.tbd_ids == []


@pytest.mark.xfail(reason="The new data layout (datav2) is not implemented yet.", strict=True)
def test_updiff_uptodate(project_with_files__datav2, remote_server):
    """
    Test that the updiff method returns an empty list of ids if the local data is up-to-date.
    """
    # Check for updates.
    updiff_result = project_with_files__datav2.updiff()
    print(project_with_files__datav2.data_dir)
    assert updiff_result.tbd_ids == {}


def test_updiff_remote_removal__datav1(project_with_files__datav1, remote_server_changed):
    """
    Test that the remote-removed ids are handled properly.
    """
    assert sorted(os.listdir(project_with_files__datav1.data_dir)) == [
        "hs01.pdb.gz",
        "hs02.pdb.gz",
        "hs03.pdb.gz",
        "rn01.pdb.gz",
        "rn02.pdb.gz",
    ]
    # Check for updates.
    updiff_result = project_with_files__datav1.updiff()
    assert updiff_result.tbd_ids == []
    assert updiff_result.removed_ids == ["rn02"]
    # The requests.get() method should be called two times, since there are two queries.
    assert len(remote_server_changed.calls) == 2

    # Call handle_removed.
    project_with_files__datav1.handle_removed(updiff_result)
    # Check that the local file is marked as obsolete (removed remotely).
    assert sorted(os.listdir(project_with_files__datav1.data_dir)) == [
        "hs01.pdb.gz",
        "hs02.pdb.gz",
        "hs03.pdb.gz",
        "rn01.pdb.gz",
        "rn02.pdb.gz.obsolete",
    ]
