"""
Unit tests for the project module.
"""
# 3rd party
import pytest
import requests

# My stuff
from project import Project


@pytest.fixture
def empty_project(tmp_path):
    """Return an empty project."""
    # Create a project in a temporary directory.
    queries = tmp_path / 'queries'
    queries.mkdir()
    # Create a fake query file.
    query_file1 = queries / 'Homo_sapiens.json'
    query_file2 = queries / 'Rattus_norvegicus.json'
    query_file1.write_text('{"query": {"query_type": "terminal", "search_type": "text", "value": "Homo sapiens"}}')
    query_file2.write_text('{"query": {"query_type": "terminal", "search_type": "text", "value": "Rattus norvegicus"}}')
    return Project(tmp_path)


# custom class to be the mock return value of requests.get()
class MockResponseOK:
    """Mock response class for requests.get()."""

    @staticmethod
    def json():
        """Abstract method."""
        raise NotImplementedError

    @staticmethod
    def raise_for_status():
        """Don't raise anything, since the response is OK."""

    # mock status_code
    status_code = 200


class MockResponseHomoSapiens(MockResponseOK):
    """Mock response class for requests.get() when the query is for Homo sapiens."""

    @staticmethod
    def json():
        """Return a dictionary."""
        return {"result_set": [{"identifier": "hs01"}, {"identifier": "hs02"}]}


class MockResponseRattusNorvegicus(MockResponseOK):
    """Mock response class for requests.get() when the query is for Rattus norvegicus."""

    @staticmethod
    def json():
        """Return a dictionary."""
        return {"result_set": [{"identifier": "rn01"}, {"identifier": "rn02"}]}


class MockResponseNoContent:
    """Mock response class for requests.get()."""
    @staticmethod
    def json():
        """Return an empty dictionary."""
        return {}

    @staticmethod
    def raise_for_status():
        """Don't raise anything, since the response is OK."""

    # mock status_code
    status_code = 204


# monkeypatched requests.get moved to a fixture
@pytest.fixture
def mock_response_ok(monkeypatch):
    """Requests.get() mocked to return a couple of ids."""

    def mock_get(query_url, **kwargs):  # pylint: disable=unused-argument
        """Mock requests.get()."""
        if "Homo sapiens" in query_url:
            return MockResponseHomoSapiens()
        if "Rattus norvegicus" in query_url:
            return MockResponseRattusNorvegicus()
        return MockResponseOK()

    monkeypatch.setattr(requests, "get", mock_get)


def test_project_non_existing_directory():
    """Test the creation of a project raises an exception if the directory does not exist."""
    # Create a project in a non-existing directory.
    with pytest.raises(FileNotFoundError):
        Project('non-existing-directory')


def test_fetch_the_first_time(empty_project, mock_response_ok):  # pylint: disable=redefined-outer-name, unused-argument
    """
    Test that the first time the project is fetched, all the remote ids are considered to be downloaded.
    """
    tbd_ids, removed_ids = empty_project.fetch()
    assert set(tbd_ids) == {'hs01', 'hs02', 'rn01', 'rn02'}
    assert removed_ids == []


def test_second_fetch_same_results(empty_project,  # pylint: disable=redefined-outer-name, unused-argument
                                   mock_response_ok):  # pylint: disable=redefined-outer-name, unused-argument
    """
    Test two subsequent fetches with no download.
    The second fetch (which loads ids from the local cache) should return the same ids as the first one.
    The second fetch should not call requests.get().

    If the test fails, it could be indicating that the local cache is not working properly.
    """
    # First fetch.
    tbd_ids, removed_ids = empty_project.fetch()
    assert set(tbd_ids) == {'hs01', 'hs02', 'rn01', 'rn02'}
    assert removed_ids == []

    # NB: nothing is downloaded.

    # Second fetch.
    tbd_ids, removed_ids = empty_project.fetch()
    assert set(tbd_ids) == {'hs01', 'hs02', 'rn01', 'rn02'}
    assert removed_ids == []

    # The second fetch should not call requests.get()
    # how to test this? Maybe with pytest-mock?
