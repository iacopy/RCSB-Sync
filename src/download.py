"""
Download PDB files from the RCSB website.
"""
from functools import partial
from multiprocessing import Pool

from typing import List

import os
import requests
import time

DOWNLOAD_URL = 'https://files.rcsb.org/download/'
MAX_PROCESSES = os.cpu_count()
DEFAULT_PROCESSES = 2


def chunks(lst, n):
    """
    Yield successive n-sized chunks from lst.
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def download_pdb(pdb_id, directory: str, compressed: bool=True) -> str:
    """
    Download a PDB file from the RCSB website.

    :param pdb_id: PDB ID.
    :return: Path to the downloaded file.
    """
    gzip_ext = '.gz' if compressed else ''
    # Documentation URL: https://www.rcsb.org/pdb/files/
    pdb_url = DOWNLOAD_URL + pdb_id + '.pdb' + gzip_ext
    # print('Downloading PDB file from RCSB website:', pdb_url)
    response = requests.get(pdb_url)
    if response.status_code == 404:
        print(f'PDB file not found: {pdb_id}')
        return
    response.raise_for_status()
    # Save the PDB file.
    dest = os.path.join(directory, pdb_id + '.pdb' + gzip_ext)
    with open(dest, 'wb') as file_pointer:
        file_pointer.write(response.content)
    return dest


# Use multiprocessing to download (typically thousands of) PDB files in parallel.
def parallel_download(pdb_ids, directory: str, compressed: bool=True, n_jobs=DEFAULT_PROCESSES) -> None:
    """
    Download PDB files from the RCSB website in parallel.

    :param pdb_ids: List of PDB IDs.
    :param directory: Directory to store the downloaded files.
    :param compressed: Whether to download compressed files.
    :param n_jobs: Number of processes to use (default: 2).
    """
    # Create the directory if it does not exist.
    if not os.path.exists(directory):
        os.makedirs(directory)
    # Download the PDB files in parallel.
    with Pool(processes=n_jobs) as pool:
        ret = pool.map(partial(download_pdb, directory=directory, compressed=compressed), pdb_ids)
        # remove None values
        return [x for x in ret if x is not None]


def download(pdb_ids: list,
             directory: str,
             compressed: bool=True,
             n_jobs=DEFAULT_PROCESSES,
             chunk_len: int=50) -> None:
    """
    Download PDB files from the RCSB website.

    :param pdb_ids: List of PDB IDs.
    :param directory: Directory to store the downloaded files.
    :param compressed: Whether to download compressed files.
    :param n_jobs: Number of processes to use (default: 2).
    """
    n_ids = len(pdb_ids)
    downloaded_size = 0
    n_downloaded = 0
    start_time = time.time()
    # Subdivide the list of PDB IDs into chunks and download each chunk in parallel.
    for i, chunk in enumerate(chunks(pdb_ids, chunk_len)):
        print(f'Downloading chunk {i + 1}/{n_ids // chunk_len}: {len(chunk)} PDBs each with {n_jobs} processes')
        # Download the chunk of PDB IDs.
        downloaded_chunk = parallel_download(chunk, directory, compressed, n_jobs)

        downloaded_size += sum(os.path.getsize(file_path) for file_path in downloaded_chunk)
        n_downloaded += len(chunk)
        progress = n_downloaded / n_ids

        # Report the global progress and the expected time to complete (based on the number of PDB files to be downloaded).
        eta_min = ((time.time() - start_time) / n_downloaded) * (n_ids - n_downloaded) / 60
        print(f'Downloaded {n_downloaded}/{n_ids} files ({progress:.2%}) - ETA: {eta_min:.2f} min ⏳')
