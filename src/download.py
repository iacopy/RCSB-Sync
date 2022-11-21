"""
Download PDB files from the RCSB website.

While you can use this module directly, it is intended to be used by the
higher-level modules (e.g. the ``project`` module which downloads PDB files
of a given project, to keep the local working directory up-to-date).
"""
# Standard Library
import logging
import os
import time
from collections import namedtuple
from functools import partial
from multiprocessing import Pool
from typing import List

# 3rd party
import requests

# My stuff
from utils import _human_readable_time

DOWNLOAD_URL_RCSB = "https://files.rcsb.org/download/"
DOWNLOAD_URL_ALPHAFOLD = "https://alphafold.ebi.ac.uk/files/"
ALPHAFOLD_SUFFIX = "model_v4"
# e.g. https://alphafold.ebi.ac.uk/files/AF-P01308-F1-model_v4.pdb

MAX_PROCESSES = os.cpu_count()
DEFAULT_PROCESSES = 1
#: This number impact the frequency of progress updates.
#: It is the number of PDB files to download before a progress update is printed if a single process is used.
#: This is scaled automatically to the number of processes used to keep the progress updates constant.
CHUNK_LEN_PER_PROCESS = 20

PDBDownloadResult = namedtuple("PDBDownloadResult", ["pdb_id", "pdb_url", "local_path", "status_code"])


def _chunks(lst, num):
    """
    Yield successive n-sized chunks from lst.
    """
    for i in range(0, len(lst), num):
        yield lst[i : i + num]


def is_alphafold_id(pdb_id: str) -> bool:
    """
    Check whether the PDB ID is an AlphaFold ID.
    """
    if pdb_id.startswith("AF"):
        assert pdb_id.startswith(
            "AF_AF"
        ), f"Unexpected AlphaFold ID (should start with 'AF_AF'): {pdb_id}"
    return pdb_id.startswith("AF_")


def alphafold_id_to_file(pdb_id: str) -> str:
    """
    Convert an AlphaFold ID to the corresponding PDB file name.

    NB: there are gigantic protein like https://www.rcsb.org/uniprot/Q8WZ42

    >>> alphafold_id_to_file("AF_AFP08437F1")
    'AF-P08437-F1-model_v4.pdb'
    >>> alphafold_id_to_file("AF_AFP01308F2")
    'AF-P01308-F2-model_v4.pdb'
    >>> alphafold_id_to_file("AF_AFQ8WZ42F166")
    'AF-Q8WZ42-F166-model_v4.pdb'
    """
    last_f = pdb_id.rfind("F")
    return f"AF-{pdb_id[5:last_f]}-{pdb_id[last_f:]}-{ALPHAFOLD_SUFFIX}.pdb"


def pdb_id_to_filename(pdb_id: str) -> str:
    """
    Convert a PDB ID to the corresponding PDB file name.

    >>> pdb_id_to_filename("1abc")
    '1abc.pdb'
    >>> pdb_id_to_filename("1abc")
    '1abc.pdb'
    >>> pdb_id_to_filename("AF_AFP01308F1")
    'AF-P01308-F1-model_v4.pdb'
    >>> pdb_id_to_filename("AF_AFQ8WZ42F166")
    'AF-Q8WZ42-F166-model_v4.pdb'
    """
    if is_alphafold_id(pdb_id):
        return alphafold_id_to_file(pdb_id)
    return f"{pdb_id}.pdb"


def filename_to_pdb_id(filename: str) -> str:
    """
    Convert a PDB file name to the corresponding PDB ID.

    >>> filename_to_pdb_id("1abc.pdb")
    '1abc'
    >>> filename_to_pdb_id("1abc.pdb.gz")
    '1abc'
    >>> filename_to_pdb_id("AF-P01308-F1-model_v4.pdb")
    'AF_AFP01308F1'
    >>> filename_to_pdb_id("AF-Q8WZ42-F166-model_v4.pdb")
    'AF_AFQ8WZ42F166'
    """
    if filename.startswith("AF-"):
        # e.g. AF-P01308-F1-model_v4.pdb
        return "AF_AF" + filename[3 : -len(f"-{ALPHAFOLD_SUFFIX}.pdb")].replace("-", "")
    # e.g. 1abc.pdb
    return filename.split(".")[0]


def get_download_url(pdb_id: str) -> str:
    """
    Based on the PDB ID, return the right URL to download the PDB file.
    """
    if is_alphafold_id(pdb_id):
        return DOWNLOAD_URL_ALPHAFOLD + alphafold_id_to_file(pdb_id)
    return f"{DOWNLOAD_URL_RCSB}{pdb_id}.pdb"


def download_pdb(pdb_id: str, directory: str, compressed: bool = True) -> PDBDownloadResult:
    """
    Download a PDB file from the RCSB website.

    :param pdb_id: PDB ID.
    :param directory: directory to store the downloaded file.
    :param compressed: whether to download compressed files.
    :return: path to the downloaded file.
    """
    # No logging here, because this function is called in parallel.

    # Documentation URL: https://www.rcsb.org/pdb/files/
    file_name = pdb_id_to_filename(pdb_id)

    pdb_url = get_download_url(pdb_id)
    dest = os.path.join(directory, file_name)

    # RCSB makes available compressed files, which are smaller and faster to download.
    if compressed and not is_alphafold_id(pdb_id):
        pdb_url += ".gz"
        dest += ".gz"

    response = requests.get(pdb_url, timeout=60)
    if response.status_code == 404:
        # logging.info(f"PDB file not found, error=404, id='{pdb_id}', url='{pdb_url}'")
        # Log the same but using %s to avoid formatting if the log level is not INFO.
        logging.info(
            "PDB file not found, error=404, id='%s', url='%s'", pdb_id, pdb_url
        )
        # Write an empty file to indicate that the PDB file was not found.
        content = b""
        # And append the PDB ID to the list of 404 PDB files, inside the directory.
        with open(
            os.path.join(directory, "404.txt"), "a", encoding="ascii"
        ) as file_404:
            file_404.write(f"{pdb_id}\n")
    else:
        response.raise_for_status()
        content = response.content

    # Save the PDB file.
    with open(dest, "wb") as file_pointer:
        file_pointer.write(content)
    return PDBDownloadResult(pdb_id=pdb_id, pdb_url=pdb_url, local_path=dest, status_code=response.status_code)


# Use multiprocessing to download (typically thousands of) PDB files in parallel.
def parallel_download(
    pdb_ids: List[str],
    directory: str,
    compressed: bool = True,
    n_jobs: int = DEFAULT_PROCESSES,
) -> List[PDBDownloadResult]:
    """
    Download PDB files from the RCSB website in parallel.

    :param pdb_ids: list of PDB IDs.
    :param directory: directory to store the downloaded files.
    :param compressed: whether to download compressed files.
    :param n_jobs: number of processes to use (default: 1).
    """
    # Download the PDB files in parallel.
    with Pool(processes=n_jobs) as pool:
        ret = pool.map(
            partial(download_pdb, directory=directory, compressed=compressed), pdb_ids
        )
        # remove null values
        return [pdb_res for pdb_res in ret if pdb_res.local_path != ""]


def download(
    pdb_ids: List[str],
    directory: str,
    compressed: bool = True,
    n_jobs=DEFAULT_PROCESSES,
) -> None:
    """
    Download PDB files from the RCSB website in parallel, reporting the progress.

    (actually, this is a wrapper around ``parallel_download``)

    Since we want to periodically notify the user about the progress and the ETA,
    this function just calls the parallel_download function several times with different chunks of PDB IDs,
    and when each chunk is finished, it prints the progress and the ETA.
    Since each chunk is downloaded in parallel, to have a constant rate of progress updates,
    we need to make sure that the number of chunks is a multiple of the number of processes, so that
    each process gets the same number of PDB IDs to download.

    :param pdb_ids: list of PDB IDs.
    :param directory: directory to store the downloaded files.
    :param compressed: whether to download compressed files.
    :param n_jobs: number of processes to use (default: 2).
    """

    def print_progress(
        n_downloaded: int,
        n_ids: int,
        start_time: float,
        downloaded_size: int,
        n_jobs: int,
    ) -> None:
        """
        Print the progress of the download.

        :param n_downloaded: number of PDB files already downloaded.
        :param n_ids: total number of PDB files to download.
        :param start_time: time when the download started.
        :param downloaded_size: size of the downloaded files.
        :param n_jobs: number of processes used.
        """
        progress = n_downloaded / n_ids
        # Report the global progress and the expected time to complete.
        t_sec = time.time() - start_time
        t_hs = _human_readable_time(t_sec)
        speed = n_downloaded / t_sec
        eta_sec = (t_sec / n_downloaded) * (n_ids - n_downloaded)
        eta = _human_readable_time(eta_sec)
        prog = f"{t_hs}: {n_downloaded:,}/{n_ids:,} ({progress:.2%}) files ({downloaded_size / 1e6:.2f} MB)"
        timing = f"{speed:,.1f}/s | {n_jobs}j; ETA: {eta} ⏳"
        print(f"{prog} ({timing})")

    n_ids = len(pdb_ids)
    downloaded_size = 0
    n_downloaded = 0
    start_time = time.time()

    chunk_len = CHUNK_LEN_PER_PROCESS * n_jobs
    # Subdivide the list of PDB IDs into chunks and download each chunk in parallel.
    # logging.info(f"Downloading {n_ids} PDB files")
    # logging.info(f"Number of processes: {n_jobs}")
    # logging.info(f"Chunk size: {chunk_len} PDB files")
    # logging.info(f"Compressed: {compressed}")
    # logging.info(f"Directory: {directory}")
    # Log the same but using %s instead of f-strings, so that it can be parsed by the logger.
    logging.info(
        "Downloading %s PDB files ; Number of processes: %s ; Chunk size: %s ; Compressed: %s ; Directory: %s",
        n_ids,
        n_jobs,
        chunk_len,
        compressed,
        directory,
    )
    for chunk in _chunks(pdb_ids, chunk_len):
        downloaded_chunk = parallel_download(chunk, directory, compressed, n_jobs)

        # Log the downloaded PDB files.
        for pdb_res in downloaded_chunk:
            # logging.info(f"PDB file downloaded, id='{pdb_id}', url='{pdb_url}'")
            # Log the same but using %s instead of f-strings, to avoid formatting the string
            # if the log level is higher than INFO.
            if pdb_res.status_code == 200:
                logging.info("PDB file downloaded: id='%s', url='%s'", pdb_res.pdb_id, pdb_res.pdb_url)
            else:
                logging.info(
                    "PDB file NOT FOUND: id='%s', url='%s'",
                    pdb_res.pdb_id,
                    pdb_res.pdb_url,
                )

        downloaded_size += sum(
            os.path.getsize(file_path) for _, _, file_path, _ in downloaded_chunk
        )
        n_downloaded += len(chunk)

        # Report the global progress and the expected time to complete.
        print_progress(n_downloaded, n_ids, start_time, downloaded_size, n_jobs)

    # Log the number of downloaded PDB files, the total time and the average speed.
    t_sec = time.time() - start_time
    speed = n_downloaded / t_sec
    logging.info(
        "Downloaded %s PDB files in %s (%.2f/s)",
        n_downloaded,
        _human_readable_time(t_sec),
        speed,
    )
