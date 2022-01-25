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


def retrieve_pdb_ids(query):
    """
    Retrieve the list of PDB IDs from the RCSB website, given an advanced query in json format.

    :param query: Advanced query in json format.
    :return: List of PDB IDs.
    """
    # Get the list of PDB IDs from the RCSB website, given an advanced query in json format.
    json_response = send_request(query)
    return [hit['identifier'] for hit in json_response['result_set']]


def send_request(query):
    """
    Send a request to the RCSB website and return the json response in a dictionary.
    """

    # Documentation URL: https://search.rcsb.org/#search-api
    print('Retrieving PDB IDs from RCSB website...')
    print('Query:', query)
    url_get = 'https://search.rcsb.org/rcsbsearch/v1/query?json=' + query
    response = requests.get(url_get)
    response.raise_for_status()
    return response.json()


def load_query(query_file):
    """
    Load the advanced query from a json file.

    :param query_file: Path to the json file.
    :return: Advanced query in json string format (single line).
    """
    with open(query_file, 'r', encoding='utf-8') as file_pointer:
        query = json.load(file_pointer)
    # return single line json string
    return json.dumps(query)


def main():
    """Parse arguments and run the script."""
    # Parse the command line arguments.
    parser = argparse.ArgumentParser(description='Script to download RCSB PDB IDs.')
    parser.add_argument('--query', help='Advanced query in json format or pointing to a JSON file',
                        required=True)
    parser.add_argument('--output', help='Output directory', required=True)
    args = parser.parse_args()

    # Check if the query is a file or a string.
    if args.query.endswith('.json'):
        print('Loading query from file:', args.query)
        query = load_query(args.query)

    # Retrieve the list of PDB IDs from the RCSB website, given an advanced query in json format.
    print('Retrieving PDB IDs from RCSB website...')
    ids = retrieve_pdb_ids(query)
    print(f'Found {len(ids)} PDB IDs.')

    # Store PDB IDs in a file.
    print('Storing PDB IDs into file:', args.output)
    with open(args.output, 'w', encoding='ascii') as file_pointer:
        for id_ in ids:
            file_pointer.write(id_ + '\n')


if __name__ == '__main__':
    main()
