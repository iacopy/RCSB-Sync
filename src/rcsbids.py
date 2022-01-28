"""
Retrieve the list of PDB IDs from the RCSB website, given an advanced query in json format.

Usage:

    python rcsbids.py --query query.json --output output.txt
"""
# Standard Library
import argparse
import json

# 3rd party
import requests

IDS_SEPARATOR = '\n'


def retrieve_pdb_ids(query):
    """
    Retrieve the list of PDB IDs from the RCSB website, given an advanced query in json format.

    :param query: Advanced query in json format.
    :return: List of PDB IDs.
    """
    # Get the list of PDB IDs from the RCSB website, given an advanced query in json format.
    json_response = _send_request(query)
    return [hit['identifier'] for hit in json_response['result_set']]


def _send_request(query):
    """
    Send a request to the RCSB website and return the json response in a dictionary.
    """
    # Documentation URL: https://search.rcsb.org/#search-api
    url_get = 'https://search.rcsb.org/rcsbsearch/v1/query?json=' + query
    response = requests.get(url_get)
    response.raise_for_status()
    return response.json()


def _load_query(query_file):
    """
    Load the advanced query from a json file.

    :param query_file: Path to the json file.
    :return: Advanced query in json string format (single line).
    """
    with open(query_file, 'r', encoding='utf-8') as file_pointer:
        query = json.load(file_pointer)
    # return single line json string
    return json.dumps(query)


def _store_pdb_ids(ids, dest, separator=IDS_SEPARATOR):
    # Store PDB IDs in a file.
    print('Storing PDB IDs into file:', dest)
    with open(dest, 'w', encoding='ascii') as file_pointer:
        for id_ in ids:
            file_pointer.write(id_ + separator)


def search_and_download_ids(query, output, separator=IDS_SEPARATOR):  # pragma: no cover
    """Search and download PDB IDs from the RCSB website, given an advanced query in json format.

    :param query: Path to the json file containing the advanced query.
    :param output: Path to the output file.
    """
    # Check if the query is a file or a string.
    if query.endswith('.json'):
        print('Loading query from file:', query)
        query = _load_query(query)

    # Retrieve the list of PDB IDs from the RCSB website, given an advanced query in json format.
    print('Retrieving PDB IDs from RCSB website...')
    ids = retrieve_pdb_ids(query)
    print(f'Found {len(ids)} PDB IDs.')

    # Store the list of PDB IDs in a file.
    _store_pdb_ids(ids, output, separator=separator)
    return ids


if __name__ == '__main__':
    # Parse the command line arguments.
    parser = argparse.ArgumentParser(description='Script to download RCSB PDB IDs.')
    parser.add_argument('-q', '--query', required=True, help='String or file path of json query')
    parser.add_argument('-o', '--output', help='Output directory', required=True)
    args = parser.parse_args()

    search_and_download_ids(args.query, args.output)
