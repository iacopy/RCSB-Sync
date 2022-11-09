"""
Unit tests for the project module.
"""
# My stuff
import project2


def test_updiff_the_first_time__datav2(new_project_dir, remote_server):
    """
    Test that the first time the project check for updates, all the remote ids are considered to be downloaded.
    """
    new_project = project2.Project(new_project_dir)
    diffs = new_project.updiff()

    assert diffs["Homo sapiens"].tbd_ids == ["hs01", "hs02", "hs03"]
    assert diffs["Homo sapiens"].removed_ids == []
    assert diffs["Rattus norvegicus"].tbd_ids == ["rn01", "rn02"]
    assert diffs["Rattus norvegicus"].removed_ids == []


def test_updiff_resume_rn__datav2(project_with_hs_files, remote_server):
    """
    Test that resuming a download works properly (Homo sapiens is already downloaded).
    """
    diffs = project_with_hs_files.updiff()
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
