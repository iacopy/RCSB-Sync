"""
Unit tests for the project module.
"""
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
def mocked_responses():
    """Return a mocked responses object."""
    with responses.RequestsMock() as rsps:
        yield rsps


def test_project_non_existing_directory():
    """Test the creation of a project raises an exception if the directory does not exist."""
    # Create a project in a non-existing directory.
    with pytest.raises(FileNotFoundError):
        Project('non-existing-directory')


def test_fetch_the_first_time(empty_project, mocked_responses):  # pylint: disable=redefined-outer-name, unused-argument
    """
    Test that the first time the project is fetched, all the remote ids are considered to be downloaded.
    """
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

    tbd_ids, removed_ids = empty_project.fetch()
    assert set(tbd_ids) == {'hs01', 'hs02', 'rn01', 'rn02'}
    assert removed_ids == []


def test_second_fetch_same_results(empty_project,  # pylint: disable=redefined-outer-name, unused-argument
                                   mocked_responses):  # pylint: disable=redefined-outer-name, unused-argument
    """
    Test two subsequent fetches with no download.
    The second fetch (which loads ids from the local cache) should return the same ids as the first one.
    The second fetch should not call the remote server.

    If the test fails, it could be indicating that the local cache is not working properly.
    """
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

    # First fetch.
    tbd_ids, removed_ids = empty_project.fetch()
    assert set(tbd_ids) == {'hs01', 'hs02', 'rn01', 'rn02'}
    assert removed_ids == []

    # The requests.get() method should be called two times, since there are two queries.
    assert len(mocked_responses.calls) == 2

    # Second fetch.
    tbd_ids, removed_ids = empty_project.fetch()
    assert set(tbd_ids) == {'hs01', 'hs02', 'rn01', 'rn02'}
    assert removed_ids == []

    # The second fetch should not call requests.get() (because the ids are loaded from the local cache).
    assert len(mocked_responses.calls) == 2
