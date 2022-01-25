"""
Testing module.
"""
# skip flake8 linting for this file, since it's a test file.
# flake8: noqa
# skip pylint long line check for this file, since it's a test file.
# pylint: disable=C0301

# My stuff
from rcsbids import send_request

TEST_QUERY = """{"query":{"type":"group","logical_operator":"and","nodes":[{"type":"terminal","service":"text","parameters":{"attribute":"entity_poly.rcsb_entity_polymer_type","operator":"exact_match","negation":false,"value":"Protein"}},{"type":"terminal","service":"text","parameters":{"attribute":"exptl.method","operator":"exact_match","negation":false,"value":"THEORETICAL MODEL"}}],"label":"text"},"return_type":"entry","request_options":{"pager":{"start":0,"rows":25},"scoring_strategy":"combined","sort":[{"sort_by":"score","direction":"desc"}]}}"""


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
    json_response = send_request(TEST_QUERY)
    ids = [hit['identifier'] for hit in json_response['result_set']]
    assert ids == EXPECTED_IDS
