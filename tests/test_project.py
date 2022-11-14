"""
Unit tests for the project module.
"""
# Standard Library
import os

# My stuff
import project


def test_get_status_the_first_time(new_project_dir, remote_server):
    """
    Test that the first time the project check for updates, all the remote ids are considered to be downloaded.
    """
    new_project = project.Project(new_project_dir)
    status = new_project.get_status()

    assert status["Homo_sapiens"].tbd_ids == ["hs01", "hs02", "hs03"]
    assert status["Homo_sapiens"].removed_ids == []
    assert status["Rattus_norvegicus"].tbd_ids == ["rn01", "rn02"]
    assert status["Rattus_norvegicus"].removed_ids == []


def test_get_status_resume_rn(project_with_hs_files_gz, remote_server):
    """
    Test that resuming a download works properly (Homo sapiens is already downloaded).
    """
    status = project_with_hs_files_gz.get_status()
    assert status["Homo_sapiens"].tbd_ids == []
    assert status["Homo_sapiens"].removed_ids == []
    assert status["Rattus_norvegicus"].tbd_ids == ["rn01", "rn02"]
    assert status["Rattus_norvegicus"].removed_ids == []


def test_get_status_resume_hs(project_with_rn_files, remote_server):
    """
    Test that resuming a download works properly (Rattus norvegicus is already downloaded).
    """
    status = project_with_rn_files.get_status()
    assert status["Homo_sapiens"].tbd_ids == ["hs01", "hs02", "hs03"]
    assert status["Homo_sapiens"].removed_ids == []
    assert status["Rattus_norvegicus"].tbd_ids == []
    assert status["Rattus_norvegicus"].removed_ids == []


def test_get_status_uptodate(project_with_files, remote_server):
    """
    Test that the get_status method returns an empty list of ids if the local data is up-to-date.
    """
    # Check for updates.
    status = project_with_files.get_status()
    assert status["Homo_sapiens"].tbd_ids == []
    assert status["Homo_sapiens"].removed_ids == []
    assert status["Rattus_norvegicus"].tbd_ids == []
    assert status["Rattus_norvegicus"].removed_ids == []


def test_mark_removed(project_with_files, remote_server_changed):
    """
    Test that obsolete files are properly marked.
    """
    # Check for updates.
    status = project_with_files.get_status()

    # The sync should mark the files removed from the server as obsolete.
    project_with_files.do_sync(status, n_jobs=1)

    assert sorted(
        os.listdir(os.path.join(project_with_files.data_dir, "Homo_sapiens"))
    ) == ["hs01.pdb.gz", "hs02.pdb.obsolete", "hs03.pdb"]

    # Check that the local file is marked as obsolete (removed remotely).
    assert sorted(
        os.listdir(os.path.join(project_with_files.data_dir, "Rattus_norvegicus"))
    ) == [
        "rn01.pdb.gz",
        "rn02.pdb.gz.obsolete",
    ]

    # Check that Project.get_data_files_for_query only returns the non-obsolete files.
    assert project_with_files.get_data_files_for_query("Rattus_norvegicus") == [
        "rn01.pdb.gz",
    ]


def test_mark_removed_af2(
    project_with_af2_volvox_files, remote_server_af2_volvox_removed
):
    """
    Test that obsolete files are properly marked.
    """
    # Check for updates.
    status = project_with_af2_volvox_files.get_status()

    # The sync should mark the files removed from the server as obsolete.
    project_with_af2_volvox_files.do_sync(status, n_jobs=1)

    assert sorted(
        os.listdir(os.path.join(project_with_af2_volvox_files.data_dir, "Volvox"))
    ) == [
        "5K2L.pdb",
        "5YZ6.pdb",
        "5YZK.pdb",
        "AF-P08436-F1-model_v4.pdb.obsolete",
        "AF-P08437-F1-model_v4.pdb",
        "AF-P08471-F1-model_v4.pdb.obsolete",
        "AF-P11481-F1-model_v4.pdb",
        "AF-P11482-F1-model_v4.pdb",
        "AF-P16865-F1-model_v4.pdb",
        "AF-P16866-F1-model_v4.pdb",
        "AF-P16867-F1-model_v4.pdb",
        "AF-P16868-F1-model_v4.pdb",
        "AF-P20904-F1-model_v4.pdb",
        "AF-P21997-F1-model_v4.pdb",
        "AF-P31584-F1-model_v4.pdb",
        "AF-P36841-F1-model_v4.pdb",
        "AF-P36861-F1-model_v4.pdb",
        "AF-P36862-F1-model_v4.pdb",
        "AF-P36863-F1-model_v4.pdb",
        "AF-P36864-F1-model_v4.pdb",
        "AF-P81131-F1-model_v4.pdb",
        "AF-P81132-F1-model_v4.pdb",
        "AF-Q08864-F1-model_v4.pdb",
        "AF-Q08865-F1-model_v4.pdb",
        "AF-Q10723-F1-model_v4.pdb",
        "AF-Q41643-F1-model_v4.pdb",
        "AF-Q9SBM5-F1-model_v4.pdb",
        "AF-Q9SBM8-F1-model_v4.pdb",
        "AF-Q9SBN3-F1-model_v4.pdb",
        "AF-Q9SBN4-F1-model_v4.pdb",
        "AF-Q9SBN5-F1-model_v4.pdb",
        "AF-Q9SBN6-F1-model_v4.pdb",
    ]
