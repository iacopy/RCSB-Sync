"""
Retrieve the list of PDB IDs from the RCSB website, given an advanced query in json format.

Usage
~~~~~

::

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

    :param query: advanced query in json format.
    :return: list of PDB IDs.
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

    :param query_file: path to the json file.
    :return: advanced query in json string format (single line).
    """
    with open(query_file, 'r', encoding='utf-8') as file_pointer:
        query = json.load(file_pointer)
    # return single line json string
    return json.dumps(query)


def store_pdb_ids(ids, dest, separator=IDS_SEPARATOR):
    """Store the list of PDB IDs in a file."""
    with open(dest, 'w', encoding='ascii') as file_pointer:
        for id_ in ids:
            file_pointer.write(id_ + separator)


def load_pdb_ids(pdb_ids_file):
    """
    Load the list of PDB IDs from a file.

    Automatically detect the separator used in the file, which is the 5th character.
    Then check that last character of the file is the same character.

    :param pdb_ids_file: path to the file containing the list of PDB IDs.
    """
    with open(pdb_ids_file, 'r', encoding='ascii') as file_pointer:
        ids = file_pointer.read()
    separator = ids[4]
    assert ids[-1] == separator, f'The last character of the file {pdb_ids_file} is "{ids[-1]}", not "{separator}".'
    return ids.split(separator)[:-1]


def search_and_download_ids(query, output, separator=IDS_SEPARATOR):  # pragma: no cover
    """Search and download PDB IDs from the RCSB website, given an advanced query in json format.

    :param query: path to the json file containing the advanced query.
    :param output: path to the output file.
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
    store_pdb_ids(ids, output, separator=separator)
    return ids


if __name__ == '__main__':
    # Parse the command line arguments.
    parser = argparse.ArgumentParser(description='Script to download RCSB PDB IDs.')
    parser.add_argument('-q', '--query', required=True, help='String or file path of json query')
    parser.add_argument('-o', '--output', help='Output directory', required=True)
    args = parser.parse_args()

    search_and_download_ids(args.query, args.output)
