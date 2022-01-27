"""
Download PDB files from the RCSB website.
"""
import os
import requests


def download_pdb(pdb_id, directory: str, compressed: bool=True) -> str:
    """
    Download a PDB file from the RCSB website.

    :param pdb_id: PDB ID.
    :return: Path to the downloaded file.
    """
    gzip_ext = '.gz' if compressed else ''
    # Documentation URL: https://www.rcsb.org/pdb/files/
    url_download = 'https://files.rcsb.org/download/' + pdb_id + '.pdb' + gzip_ext
    # print('Downloading PDB file from RCSB website:', url_download)
    response = requests.get(url_download)
    response.raise_for_status()
    # Save the PDB file.
    dest = os.path.join(directory, pdb_id + '.pdb' + gzip_ext)
    with open(dest, 'wb') as file_pointer:
        file_pointer.write(response.content)
    return dest
