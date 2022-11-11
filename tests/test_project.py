"""
Unit tests for the project module.
"""
# Standard Library
# Standard library
import os

# My stuff
import project


def test_updiff_the_first_time__datav2(new_project_dir, remote_server):
    """
    Test that the first time the project check for updates, all the remote ids are considered to be downloaded.
    """
    new_project = project.Project(new_project_dir)
    diffs = new_project.updiff()

    assert diffs["Homo sapiens"].tbd_ids == ["hs01", "hs02", "hs03"]
    assert diffs["Homo sapiens"].removed_ids == []
    assert diffs["Rattus norvegicus"].tbd_ids == ["rn01", "rn02"]
    assert diffs["Rattus norvegicus"].removed_ids == []


def test_updiff_resume_rn__datav2(project_with_hs_files_gz, remote_server):
    """
    Test that resuming a download works properly (Homo sapiens is already downloaded).
    """
    diffs = project_with_hs_files_gz.updiff()
    assert diffs["Homo sapiens"].tbd_ids == []
    assert diffs["Homo sapiens"].removed_ids == []
    assert diffs["Rattus norvegicus"].tbd_ids == ["rn01", "rn02"]
    assert diffs["Rattus norvegicus"].removed_ids == []


def test_updiff_resume_hs__datav2(project_with_rn_files, remote_server):
    """
    Test that resuming a download works properly (Rattus norvegicus is already downloaded).
    """
    diffs = project_with_rn_files.updiff()
    assert diffs["Homo sapiens"].tbd_ids == ["hs01", "hs02", "hs03"]
    assert diffs["Homo sapiens"].removed_ids == []
    assert diffs["Rattus norvegicus"].tbd_ids == []
    assert diffs["Rattus norvegicus"].removed_ids == []


def test_updiff_uptodate__datav2(project_with_files__datav2, remote_server):
    """
    Test that the updiff method returns an empty list of ids if the local data is up-to-date.
    """
    # Check for updates.
    updiff_result = project_with_files__datav2.updiff()
    assert updiff_result["Homo sapiens"].tbd_ids == []
    assert updiff_result["Homo sapiens"].removed_ids == []
    assert updiff_result["Rattus norvegicus"].tbd_ids == []
    assert updiff_result["Rattus norvegicus"].removed_ids == []


def test_mark_removed__datav2(project_with_files__datav2, remote_server_changed):
    """
    Test that obsolete files are properly marked.
    """
    # Check for updates.
    updiff_result = project_with_files__datav2.updiff()

    # The sync should mark the files removed from the server as obsolete.
    project_with_files__datav2.do_sync(updiff_result, n_jobs=1)

    # Check that the local file is marked as obsolete (removed remotely).
    assert sorted(
        os.listdir(
            os.path.join(project_with_files__datav2.data_dir, "Rattus norvegicus")
        )
    ) == [
        "rn01.pdb.gz",
        "rn02.pdb.gz.obsolete",
    ]

    # Check that Project.get_data_files_for_query only returns the non-obsolete files.
    assert project_with_files__datav2.get_data_files_for_query("Rattus norvegicus") == [
        "rn01.pdb.gz",
    ]
