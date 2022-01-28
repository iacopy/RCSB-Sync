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
#: This number impact the frequency of progress updates.
#: It is the number of PDB files to download before a progress update is printed if a single process is used.
#: This is scaled automatically to the number of processes used to keep the progress updates constant.
CHUNK_LEN_PER_PROCESS = 10


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
        return ''
    response.raise_for_status()
    # Save the PDB file.
    dest = os.path.join(directory, pdb_id + '.pdb' + gzip_ext)
    with open(dest, 'wb') as file_pointer:
        file_pointer.write(response.content)
    return dest


# Use multiprocessing to download (typically thousands of) PDB files in parallel.
def parallel_download(pdb_ids, directory: str, compressed: bool=True, n_jobs=DEFAULT_PROCESSES) -> List[str]:
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
        # remove null values
        return [x for x in ret if x is not '']


def download(pdb_ids: List[str],
             directory: str,
             compressed: bool=True,
             n_jobs=DEFAULT_PROCESSES) -> None:
    """
    Download PDB files from the RCSB website in parallel.

    Since we want to periodically notify the user about the progress and the ETA,
    this function just calls the parallel_download function several times with different chunks of PDB IDs,
    and when each chunk is finished, it prints the progress and the ETA.
    Since each chunk is downloaded in parallel, to have a constant rate of progress updates,
    we need to make sure that the number of chunks is a multiple of the number of processes, so that
    each process gets the same number of PDB IDs to download.

    :param pdb_ids: List of PDB IDs.
    :param directory: Directory to store the downloaded files.
    :param compressed: Whether to download compressed files.
    :param n_jobs: Number of processes to use (default: 2).
    """
    n_ids = len(pdb_ids)
    downloaded_size = 0
    n_downloaded = 0
    start_time = time.time()

    chunk_len = CHUNK_LEN_PER_PROCESS * n_jobs
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
