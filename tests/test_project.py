"""
Unit tests for the project module.
"""
# Standard Library
import os
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
def project_with_files(empty_project):  # pylint: disable=redefined-outer-name
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


def test_project_non_existing_directory():
    """Test the creation of a project raises an exception if the directory does not exist."""
    # Create a project in a non-existing directory.
    with pytest.raises(FileNotFoundError):
        Project('non-existing-directory')


def test_updiff_the_first_time(empty_project,  # pylint: disable=redefined-outer-name, unused-argument
                               mocked_responses):  # pylint: disable=redefined-outer-name, unused-argument
    """
    Test that the first time the project check for updates, all the remote ids are considered to be downloaded.
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

    tbd_ids, removed_ids = empty_project.updiff()
    assert set(tbd_ids) == {'hs01', 'hs02', 'rn01', 'rn02'}
    assert removed_ids == []


def test_second_updiff_same_results(empty_project,  # pylint: disable=redefined-outer-name, unused-argument
                                    mocked_responses):  # pylint: disable=redefined-outer-name, unused-argument
    """
    Test two subsequent updiffs with no download.
    The second updiff (which loads ids from the local cache) should return the same ids as the first one.
    The second updiff should not call the remote server.

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

    # First updiff.
    tbd_ids, removed_ids = empty_project.updiff()
    assert set(tbd_ids) == {'hs01', 'hs02', 'rn01', 'rn02'}
    assert removed_ids == []

    # The requests.get() method should be called two times, since there are two queries.
    assert len(mocked_responses.calls) == 2

    # Second updiff.
    tbd_ids, removed_ids = empty_project.updiff()
    assert set(tbd_ids) == {'hs01', 'hs02', 'rn01', 'rn02'}
    assert removed_ids == []

    # The second updiff should not call requests.get() (because the ids are loaded from the local cache).
    assert len(mocked_responses.calls) == 2


def test_removed_handling(project_with_files, mocked_responses):  # pylint: disable=redefined-outer-name
    """
    Test that the remote-removed ids are handled properly.
    """
    mocked_responses.get(
        url=f'{SEARCH_ENDPOINT_URI}',
        body='{"result_set": [{"identifier": "hs01"}, {"identifier": "hs02"}]}',
        status=200,
        content_type="application/json",
    )
    # The remote server returns a different set of ids (rn02 is removed).
    mocked_responses.get(
        url=f'{SEARCH_ENDPOINT_URI}',
        body='{"result_set": [{"identifier": "rn01"}]}',
        status=200,
        content_type="application/json",
    )

    updiff_result = project_with_files.updiff()
    assert updiff_result.tbd_ids == []
    assert updiff_result.removed_ids == ['rn02']

    # The requests.get() method should be called two times, since there are two queries.
    assert len(mocked_responses.calls) == 2

    assert sorted(os.listdir(project_with_files.data_dir)) == [
        'hs01.pdb.gz', 'hs02.pdb.gz', 'rn01.pdb.gz', 'rn02.pdb.gz']
    project_with_files.handle_removed(updiff_result)
    assert sorted(os.listdir(project_with_files.data_dir)) == [
        'hs01.pdb.gz', 'hs02.pdb.gz', 'rn01.pdb.gz', 'rn02.pdb.gz.obsolete']
