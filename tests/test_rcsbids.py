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

# 3rd party
import pytest

# My stuff
from rcsbids import _load_query
from rcsbids import load_pdb_ids
from rcsbids import retrieve_pdb_ids
from rcsbids import store_pdb_ids

# Test data
TEST_QUERY_EXP = """{
  "query": {
    "type": "terminal",
    "label": "text",
    "service": "text",
    "parameters": {
      "attribute": "rcsb_entity_source_organism.taxonomy_lineage.name",
      "operator": "exact_match",
      "negation": false,
      "value": "Verrucomicrobia subdivision 3"
    }
  },
  "return_type": "entry",
  "request_options": {
    "paginate": {
      "start": 0,
      "rows": 25
    },
    "results_content_type": [
      "experimental"
    ],
    "sort": [
      {
        "sort_by": "score",
        "direction": "desc"
      }
    ],
    "scoring_strategy": "combined"
  }
}
"""

TEST_QUERY_COMBO = """{
  "query": {
    "type": "terminal",
    "label": "text",
    "service": "text",
    "parameters": {
      "attribute": "rcsb_entity_source_organism.taxonomy_lineage.name",
      "operator": "exact_match",
      "negation": false,
      "value": "Verrucomicrobia subdivision 3"
    }
  },
  "return_type": "entry",
  "request_options": {
    "paginate": {
      "start": 0,
      "rows": 25
    },
    "results_content_type": [
      "computational",
      "experimental"
    ],
    "sort": [
      {
        "sort_by": "score",
        "direction": "desc"
      }
    ],
    "scoring_strategy": "combined"
  }
}
"""

EXPECTED_COMBO = """{
	"query_id": "9aac1a6b-cdc5-4e30-8e81-718b331ce9b3",
	"result_type": "entry",
	"total_count": 2,
	"result_set": [
		{
			"identifier": "AF_AFB9XEI9F1",
			"score": 1
		},
		{
			"identifier": "AF_AFB9XEK4F1",
			"score": 1
		}
	]
}"""


# The expected PDB IDs for the query above, which include also computational results, are from the AlphaFold DB.
EXPECTED_IDS_AF = ["AF_AFB9XEI9F1", "AF_AFB9XEK4F1"]


@pytest.mark.webtest
def test_retrieve_pdb_ids_zero():
    """
    Perform a known JSON test query and check that the expected PDB IDs are returned.

    This is an API test, not a unit test.
    This query retrieve IDs of proteins for an organism for which there are no experimental PDB entries.
    WARNING: obviously, this test will fail when the number of entries change.

    :return: None
    """
    ids = retrieve_pdb_ids(TEST_QUERY_EXP)
    assert ids == []


@pytest.mark.webtest
def test_retrieve_pdb_ids_computational():
    """
    Perform a known JSON test query and check that the expected PDB IDs are returned.

    This is an API test, not a unit test.
    This query retrieve IDs of proteins for an organism for which there are no experimental PDB entries.
    WARNING: obviously, this test will fail when the number of entries change.

    :return: None
    """
    ids = retrieve_pdb_ids(TEST_QUERY_COMBO)
    assert ids == EXPECTED_IDS_AF


def test_store_pdb_ids():
    """
    Test the store_pdb_ids function, which stores the PDB IDs in a given file.

    :return: None
    """
    store_pdb_ids(EXPECTED_IDS_AF, "tests/test_pdb_ids.txt")
    with open("tests/test_pdb_ids.txt", "r", encoding="ascii") as file_pointer:
        ids = file_pointer.read().split("\n")
    # the last line should be empty (the file should end with a newline)
    assert ids[-1] == ""
    assert ids[:-1] == EXPECTED_IDS_AF
    os.remove("tests/test_pdb_ids.txt")


def test_load_pdb_ids():
    """
    Test the load_pdb_ids function, which loads the PDB IDs from a given file.

    :return: None
    """
    store_pdb_ids(EXPECTED_IDS_AF, "tests/test_pdb_ids.txt")
    ids = load_pdb_ids("tests/test_pdb_ids.txt")
    assert ids == EXPECTED_IDS_AF
    os.remove("tests/test_pdb_ids.txt")


def test__load_query():
    """
    Test the _load_query function, which loads a query from a file.

    :return: None
    """
    expected = """{"query":{"type":"terminal","label":"text","service":"text","parameters":{"attribute":"rcsb_entity_source_organism.taxonomy_lineage.name","operator":"exact_match","negation":false,"value":"Verrucomicrobia subdivision 3"}},"return_type":"entry","request_options":{"paginate":{"start":0,"rows":25},"results_content_type":["computational","experimental"],"sort":[{"sort_by":"score","direction":"desc"}],"scoring_strategy":"combined"}}"""
    query = _load_query("tests/test_query_csm.json")
    # check that is one line and that matches the expected query
    assert len(query.split("\n")) == 1
    assert json.loads(query) == json.loads(expected)
