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
    query_file = queries / 'query_01.json'
    query_file.write_text('{"query": {"query_type": "terminal", "search_type": "text", "value": "Homo sapiens"}}')
    return Project(tmp_path)


# custom class to be the mock return value of requests.get()
class MockResponseOK:
    """Mock response class for requests.get()."""
    @staticmethod
    def json():
        """Return a dictionary."""
        return {"result_set": [{"identifier": "1abc"}, {"identifier": "2def"}]}

    @staticmethod
    def raise_for_status():
        """Don't raise anything, since the response is OK."""

    # mock status_code
    status_code = 200


# monkeypatched requests.get moved to a fixture
@pytest.fixture
def mock_response_ok(monkeypatch):
    """Requests.get() mocked to return a couple of ids."""

    def mock_get(*args, **kwargs):  # pylint: disable=unused-argument
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
    assert tbd_ids == ['1abc', '2def']
    assert removed_ids == []
