"""
Fixtures.
"""
from pathlib import Path

import pytest
import responses

from project import Project
from rcsbids import SEARCH_ENDPOINT_URI

# Fake json queries
HS_QUERY = '{"query": {"query_type": "terminal", "search_type": "text", "value": "Homo sapiens"}}'
RN_QUERY = '{"query": {"query_type": "terminal", "search_type": "text", "value": "Rattus norvegicus"}}'


@pytest.fixture
def empty_project(tmp_path):
    """Return an empty project."""
    # Create a project in a temporary directory.
    queries = tmp_path / 'queries'
    queries.mkdir()
    # Create a fake query file.
    query_file1 = queries / 'Homo_sapiens.json'
    query_file2 = queries / 'Rattus_norvegicus.json'
    query_file1.write_text(HS_QUERY)
    query_file2.write_text(RN_QUERY)
    return Project(tmp_path)


@pytest.fixture
def project_with_files(empty_project):
    """Return a project with some downloaded files."""
    # add pdb.gz files inside the project directory
    hs01 = Path(empty_project.data_dir, 'hs01.pdb.gz')
    hs02 = Path(empty_project.data_dir, 'hs02.pdb.gz')
    rn01 = Path(empty_project.data_dir, 'rn01.pdb.gz')
    rn02 = Path(empty_project.data_dir, 'rn02.pdb.gz')
    hs01.write_text('hs01', encoding='ascii')
    hs02.write_text('hs02', encoding='ascii')
    rn01.write_text('rn01', encoding='ascii')
    rn02.write_text('rn02', encoding='ascii')
    return empty_project


@pytest.fixture
def mocked_responses():
    """Return a mocked responses object."""
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture
def remote_server(mocked_responses):
    """Return a mocked remote server with ids."""
    mocked_responses.get(
        url=f'{SEARCH_ENDPOINT_URI}',
        body='{"result_set": [{"identifier": "hs01"}, {"identifier": "hs02"}]}',
        status=200,
        content_type="application/json",
    )
    mocked_responses.get(
        url=f'{SEARCH_ENDPOINT_URI}',
        body='{"result_set": [{"identifier": "rn01"}, {"identifier": "rn02"}]}',
        status=200,
        content_type="application/json",
    )
    return mocked_responses
