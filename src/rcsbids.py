"""
Retrieve the list of PDB IDs from the RCSB website, given an advanced query in json format.

Usage
~~~~~

::

    python rcsbids.py --query query.json --output output.txt
"""
# Standard Library
import argparse

# 3rd party
import requests

# My stuff
from utils import _load_query

# Constants
IDS_SEPARATOR = "\n"
# Documentation URL: https://search.rcsb.org/#search-api
SEARCH_ENDPOINT_URI = "https://search.rcsb.org/rcsbsearch/v2/query"


def retrieve_pdb_ids(query: str) -> list:
    """
    Retrieve the list of PDB IDs from the RCSB website, given an advanced query in json format.

    :param query: advanced query in json format.
    :return: list of PDB IDs.
    """
    json_response = _send_request(query)
    return [hit["identifier"] for hit in json_response.get("result_set", [])]


def _send_request(query: str) -> dict:
    """
    Send a request to the RCSB website and return the json response in a dictionary.

    :param query: advanced query in json format.
    """
    url_get = f"{SEARCH_ENDPOINT_URI}?json={query}"
    response = requests.get(url_get, timeout=60)
    response.raise_for_status()
    # Handle 204 No Content response
    return {} if response.status_code == 204 else response.json()


def store_pdb_ids(ids: list, dest: str) -> None:
    """Store the list of PDB IDs in a file.

    :param ids: list of PDB IDs.
    :param dest: path to the output file.
    """
    with open(dest, "w", encoding="ascii") as file_pointer:
        for id_ in ids:
            file_pointer.write(id_ + IDS_SEPARATOR)


def load_pdb_ids(pdb_ids_file: str) -> list:
    """
    Load the list of PDB IDs from a file.

    :param pdb_ids_file: path to the file containing the list of PDB IDs.
    :return: list of PDB IDs.
    """
    return [line.strip() for line in open(pdb_ids_file, "r", encoding="ascii")]


def search_and_download_ids(query: str) -> list:  # pragma: no cover
    """Search and download PDB IDs from the RCSB website, given an advanced query in json format.

    :param query: path to the json file containing the advanced query (or the advanced query in json string format).
    :return: list of PDB IDs.
    """
    # Check if the query is a file or a string.
    if query.endswith(".json"):
        # print("Loading query from file:", query) # DEBUG
        query = _load_query(query)

    # Retrieve the list of PDB IDs from the RCSB website, given an advanced query in json format.
    return retrieve_pdb_ids(query)


if __name__ == "__main__":
    # Parse the command line arguments.
    parser = argparse.ArgumentParser(description="Script to download RCSB PDB IDs.")
    parser.add_argument(
        "-q",
        "--query",
        default="tests/test-project-nodata/queries/Rabbitpox virus.json",
        help="String or file path of json query",
    )
    args = parser.parse_args()

    for pdb_id in search_and_download_ids(args.query):
        print(pdb_id)
