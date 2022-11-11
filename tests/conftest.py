"""
Fixtures.
"""
# Standard Library
import os
import shutil
from pathlib import Path

# 3rd party
import pytest
import responses
import testutils

# My stuff
import project
from rcsbids import SEARCH_ENDPOINT_URI

# Fake json queries
HS_QUERY = '{"query": {"query_type": "terminal", "search_type": "text", "value": "Homo sapiens"}}'
RN_QUERY = '{"query": {"query_type": "terminal", "search_type": "text", "value": "Rattus norvegicus"}}'


@pytest.fixture
def new_project_dir(tmp_path):
    """Return a directory with queries but no data."""
    # Create project files in a temporary directory.
    queries = tmp_path / "queries"
    queries.mkdir()
    # Create a fake query file.
    query_file1 = queries / "Homo sapiens.json"
    query_file2 = queries / "Rattus norvegicus.json"
    query_file1.write_text(HS_QUERY)
    query_file2.write_text(RN_QUERY)
    return tmp_path


@pytest.fixture
def project_nodata_cleanup():
    """
    Fixture to clean up the data directory after the test.
    """
    project_dir = os.path.join(os.path.dirname(__file__), "test-project-nodata")
    # pre-checks
    testutils.check_nodata(project_dir)

    yield project_dir

    # cleanup of downloaded files and cache
    testutils.clean_cache_files(project_dir)
    # remove the data directory
    data_dir = os.path.join(project_dir, "data")
    # Completely remove the data directory, even if it is not empty.
    if os.path.isdir(data_dir):
        shutil.rmtree(data_dir)


@pytest.fixture
def project_with_files__datav2(new_project_dir):
    """Return a project with some downloaded files."""
    # add pdb.gz files inside the project directory
    prj = project.Project(new_project_dir)
    hs_dir = Path(prj.data_dir, "Homo sapiens")
    # hs_dir.mkdir(parents=True)
    hs01 = Path(hs_dir, "hs01.pdb.gz")
    hs02 = Path(hs_dir, "hs02.pdb")
    hs03 = Path(hs_dir, "hs03.pdb")
    hs01.write_text("hs01", encoding="ascii")
    hs02.write_text("hs02", encoding="ascii")
    hs03.write_text("hs03", encoding="ascii")
    rn_dir = Path(prj.data_dir, "Rattus norvegicus")
    # rn_dir.mkdir(parents=True)
    rn01 = Path(rn_dir, "rn01.pdb.gz")
    rn02 = Path(rn_dir, "rn02.pdb.gz")
    rn01.write_text("rn01", encoding="ascii")
    rn02.write_text("rn02", encoding="ascii")
    return prj


@pytest.fixture
def project_with_hs_files_gz(new_project_dir):
    """Return a project with 3 Homo sapiens fake pdb.gz files."""
    prj = project.Project(new_project_dir)
    # add pdb.gz files inside the project directory
    hs_dir = Path(prj.data_dir, "Homo sapiens")
    hs01 = Path(hs_dir, "hs01.pdb.gz")
    hs02 = Path(hs_dir, "hs02.pdb.gz")
    hs03 = Path(hs_dir, "hs03.pdb.gz")
    hs01.write_text("hs01", encoding="ascii")
    hs02.write_text("hs02", encoding="ascii")
    hs03.write_text("hs03", encoding="ascii")
    return prj


@pytest.fixture
def project_with_rn_files(new_project_dir):
    """Return a project with Rattus norvegicus fake pdb files."""
    prj = project.Project(new_project_dir)
    # add pdb.gz files inside the project directory
    rn_dir = Path(prj.data_dir, "Rattus norvegicus")
    rn01 = Path(rn_dir, "rn01.pdb")
    rn02 = Path(rn_dir, "rn02.pdb")
    rn01.write_text("rn01", encoding="ascii")
    rn02.write_text("rn02", encoding="ascii")
    return prj


def result_set(ids):
    """Return a json string with a list of ids."""
    return (
        '{"result_set": ['
        + ", ".join([f'{{"identifier": "{id_}"}}' for id_ in ids])
        + "]}"
    )


def make_search_response(ids):
    """Return an OK search response object with a list of ids."""
    return responses.Response(
        method="GET",
        url=f"{SEARCH_ENDPOINT_URI}",
        body=result_set(ids),
        status=200,
        content_type="application/json",
    )


@pytest.fixture
def mocked_responses():
    """Return a mocked responses object."""
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture
def remote_server(mocked_responses):
    """Return a mocked remote server with ids."""
    # Add responses to the mocked server for the queries.
    mocked_responses.add(make_search_response(["hs01", "hs02", "hs03"]))
    # Second query.
    mocked_responses.add(make_search_response(["rn01", "rn02"]))
    return mocked_responses


@pytest.fixture
def remote_server_changed(mocked_responses):
    """Return a mocked remote server with an id removed."""
    # Add responses to the mocked server for the queries ("hs02" is removed).
    mocked_responses.add(make_search_response(["hs01", "hs03"]))
    # Second query ("rn02" is removed).
    mocked_responses.add(make_search_response(["rn01"]))
    return mocked_responses
