"""
Check utilities.
"""
# Standard Library
import os


def list_files(directory):
    """
    List files in directory.

    Cleanup .DS_Store before checking
    """
    if os.path.isfile(os.path.join(directory, ".DS_Store")):
        os.remove(os.path.join(directory, ".DS_Store"))
    return os.listdir(directory)


def check_nodata(project_dir):
    """
    Check that the project directory contains no data.
    """
    assert os.path.isdir(
        project_dir
    ), f"Project directory {project_dir} does not exist."
    # check that the data directory does not exist
    assert not os.path.isdir(
        os.path.join(project_dir, "data")
    ), f"Data directory {os.path.join(project_dir, 'data')} exists."
    # check the main level: no files, only the queries directory
    assert list_files(project_dir) == [
        "queries"
    ], f"Wrong files in {project_dir}: {os.listdir(project_dir)}"
    # check queries directory contain 2 json files
    queries_dir = os.path.join(project_dir, "queries")
    assert sorted(os.listdir(queries_dir)) == [
        "Rabbitpox_virus.json",
        "Radianthus_crispus.json",
    ]


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
