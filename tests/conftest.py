"""
Fixtures.
"""
# Standard Library
from pathlib import Path

# 3rd party
import pytest
import responses

# My stuff
from project import Project
from rcsbids import SEARCH_ENDPOINT_URI

# Fake json queries
HS_QUERY = '{"query": {"query_type": "terminal", "search_type": "text", "value": "Homo sapiens"}}'
RN_QUERY = '{"query": {"query_type": "terminal", "search_type": "text", "value": "Rattus norvegicus"}}'


@pytest.fixture
def new_project(tmp_path):
    """Return a directory with queries but no data."""
    # Create project files in a temporary directory.
    queries = tmp_path / "queries"
    queries.mkdir()
    # Create a fake query file.
    query_file1 = queries / "Homo sapiens.json"
    query_file2 = queries / "Rattus norvegicus.json"
    query_file1.write_text(HS_QUERY)
    query_file2.write_text(RN_QUERY)
    return Project(tmp_path)


@pytest.fixture
def project_with_files__datav1(new_project):
    """Return a project with some downloaded files."""
    # add pdb.gz files inside the project directory
    hs01 = Path(new_project.data_dir, "hs01.pdb.gz")
    hs02 = Path(new_project.data_dir, "hs02.pdb.gz")
    hs03 = Path(new_project.data_dir, "hs03.pdb.gz")
    rn01 = Path(new_project.data_dir, "rn01.pdb.gz")
    rn02 = Path(new_project.data_dir, "rn02.pdb.gz")
    hs01.write_text("hs01", encoding="ascii")
    hs02.write_text("hs02", encoding="ascii")
    hs03.write_text("hs03", encoding="ascii")
    rn01.write_text("rn01", encoding="ascii")
    rn02.write_text("rn02", encoding="ascii")
    return new_project


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
    # Add responses to the mocked server for the queries.
    mocked_responses.add(make_search_response(["hs01", "hs02", "hs03"]))
    # Second query.
    mocked_responses.add(make_search_response(["rn01"]))
    return mocked_responses
