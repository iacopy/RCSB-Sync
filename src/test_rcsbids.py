"""
Testing the functions of the rcsbids module,
which are used to retrieve the PDB IDs from the RCSB database.
"""
# skip flake8 linting for this file, since it's a test file.
# flake8: noqa
# skip pylint long line check for this file, since it's a test file.
# pylint: disable=C0301

# Standard Library
import json
import os

# My stuff
from rcsbids import _load_query
from rcsbids import load_pdb_ids
from rcsbids import retrieve_pdb_ids
from rcsbids import store_pdb_ids

TEST_QUERY = _load_query('queries/test_query.json')
# A real query, which returns 6 entries.
EXPECTED_QUERY = """{"query":{"type":"group","logical_operator":"and","nodes":[{"type":"terminal","service":"text","parameters":{"attribute":"entity_poly.rcsb_entity_polymer_type","operator":"exact_match","negation":false,"value":"Protein"}},{"type":"terminal","service":"text","parameters":{"attribute":"exptl.method","operator":"exact_match","negation":false,"value":"THEORETICAL MODEL"}}],"label":"text"},"return_type":"entry","request_options":{"pager":{"start":0,"rows":25},"scoring_strategy":"combined","sort":[{"sort_by":"score","direction":"desc"}]}}"""

# The server response to the query above.
EXPECTED_JSON_RESPONSE = {
    "query_id": "ed8fc6b7-7a04-4733-ba33-88740de1f970",
    "result_type": "entry",
    "total_count": 6,
    "result_set": [{
        "identifier": "1DWL",
        "score": 1.0,
        "services": [{
            "service_type": "text",
            "nodes": [{
                "node_id": 31667,
                "original_score": 10.145727157592773,
                "norm_score": 1.0
            }]
        }]
    }, {
        "identifier": "1E08",
        "score": 1.0,
        "services": [{
            "service_type": "text",
            "nodes": [{
                "node_id": 31667,
                "original_score": 10.145727157592773,
                "norm_score": 1.0
            }]
        }]
    }, {
        "identifier": "1GX7",
        "score": 1.0,
        "services": [{
            "service_type": "text",
            "nodes": [{
                "node_id": 31667,
                "original_score": 10.145727157592773,
                "norm_score": 1.0
            }]
        }]
    }, {
        "identifier": "1OLN",
        "score": 1.0,
        "services": [{
            "service_type": "text",
            "nodes": [{
                "node_id": 31667,
                "original_score": 10.145727157592773,
                "norm_score": 1.0
            }]
        }]
    }, {
        "identifier": "1UR6",
        "score": 1.0,
        "services": [{
            "service_type": "text",
            "nodes": [{
                "node_id": 31667,
                "original_score": 10.145727157592773,
                "norm_score": 1.0
            }]
        }]
    }, {
        "identifier": "1VYC",
        "score": 1.0,
        "services": [{
            "service_type": "text",
            "nodes": [{
                "node_id": 31667,
                "original_score": 10.145727157592773,
                "norm_score": 1.0
            }]
        }]
    }]
}

EXPECTED_IDS = ['1DWL', '1E08', '1GX7', '1OLN', '1UR6', '1VYC']


def test_retrieve_pdb_ids():
    """
    Perform a known JSON test query and check that the expected PDB IDs are returned.

    This is an API test, not a unit test.
    This query retrieve IDs of proteins whose the experimental method is THEORETICAL MODEL (I choose this because it returns only 6 entries, currently).
    NB: obviously, this test will fail when the number of entries change.

    :return: None
    """
    ids = retrieve_pdb_ids(TEST_QUERY)
    assert ids == EXPECTED_IDS


def test_store_pdb_ids():
    """
    Test the store_pdb_ids function, which stores the PDB IDs in a given file.

    :return: None
    """
    store_pdb_ids(EXPECTED_IDS, 'test_pdb_ids.txt')
    with open('test_pdb_ids.txt', 'r', encoding='ascii') as file_pointer:
        ids = file_pointer.read().split('\n')
    # the last line should be empty (the file should end with a newline)
    assert ids[-1] == ''
    assert ids[:-1] == EXPECTED_IDS
    os.remove('test_pdb_ids.txt')


def test_load_pdb_ids():
    """
    Test the load_pdb_ids function, which loads the PDB IDs from a given file.

    :return: None
    """
    store_pdb_ids(EXPECTED_IDS, 'test_pdb_ids.txt')
    ids = load_pdb_ids('test_pdb_ids.txt')
    assert ids == EXPECTED_IDS
    os.remove('test_pdb_ids.txt')


def test__load_query():
    """
    Test the _load_query function, which loads a query from a file.

    :return: None
    """
    query = _load_query('queries/test_query.json')
    # check that is one line and that matches the expected query
    assert len(query.split('\n')) == 1
    assert json.loads(query) == json.loads(EXPECTED_QUERY)
