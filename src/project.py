"""
Download protein structures for a project from the RCSB PDB database.

Usage
~~~~~

::

    python project.py project_dir [--n_jobs n_jobs]

Algorithm
~~~~~~~~~

1. Start by downloading the RCSB PDB IDs for the project, using the queries in the ``queries`` directory.
2. Before downloading the PDB files, check which PDB files are already in the local project directory,
   and skip them.
3. Some local PDB files are not in the RCSB database anymore, so we mark them with a suffix (for example '.obsolete').
4. Print a report of:

   - the number of DB files already in the project directory;
   - the number of PDB files that will be downloaded;
   - the removed/obsolete PDB files.

5. Download the PDB files corresponding to the RCSB PDB IDs which are not already in the project directory.
6. During the download, report the global progress and the expected time to completion.

Directory structure
~~~~~~~~~~~~~~~~~~~

The directory structures of a project is as follows::

    .
    ├── ProjectName
    │   ├── queries
    │   │   ├── query_0.json
    │   │   ├── query_1.json
    │   │   └── query_2.json
    │   └── data
    │       ├── query_01
    │       │   ├── 1abc.pdb
    │       │   ├── 1abd.pdb
    │       │   └── 1abe.pdb
    │       └── query_02
    │           ├── 1abf.pdb
    │           ├── 1abg.pdb
    │           └── 1abh.pdb
    └── README.md
"""
# Standard Library
import argparse
import datetime
import logging
import os
import time
from collections import namedtuple
from typing import Dict
from typing import List

# 3rd party
from tabulate import tabulate

# My stuff
import download
import rcsbids

IDS_SEPARATOR = "\n"
SUFFIX_REMOVED = ".obsolete"
PDB_EXT = ".pdb"
COMPRESSED_EXT = ".pdb.gz"

# Settings for the parallel download.
DEFAULT_JOBS = 1
MAX_JOBS = os.cpu_count()


# Named tuple to store the fetch results.
DirStatus = namedtuple(
    "DirStatus", ["n_local", "n_remote", "tbd_ids", "removed_ids", "zero_ids"]
)
ProjectStatus = Dict[str, DirStatus]


def pformat_status(project_status: ProjectStatus) -> str:
    """
    Create a nice string table with the status of the project.

    :param project_status: dictionary with the status of the project.
    :return: a string with the table.
    """
    table = []
    for query_name, dir_status in project_status.items():
        table.append(
            [
                query_name,
                dir_status.n_local,
                len(dir_status.zero_ids),
                dir_status.n_local - len(dir_status.zero_ids),
                dir_status.n_remote,
                len(dir_status.tbd_ids),
                len(dir_status.removed_ids),
            ]
        )
    # Add a total row.
    table.append(
        [
            "TOTAL",
            sum(row[1] for row in table),
            sum(row[2] for row in table),
            sum(row[3] for row in table),
            sum(row[4] for row in table),
            sum(row[5] for row in table),
            sum(row[6] for row in table),
        ]
    )

    return tabulate(
        table,
        headers=[
            "Query",
            "Local",
            "Zero size",
            "Non-zero",
            "Remote",
            "To download",
            "Removed",
        ],
        intfmt=",",
    ).replace(",", " ")


class Project:
    """
    Keep synced the data directory with the remote RCSB database.
    """

    def __init__(self, directory: str):
        self.directory = directory
        self.queries_dir = os.path.join(self.directory, "queries")
        self.data_dir = os.path.join(self.directory, "data")

        # Create the data directory if it does not exist.
        if not os.path.isdir(self.data_dir):
            logging.info("Creating data directory: %s", self.data_dir)
            os.mkdir(self.data_dir)

        # Create the query data directories if they don't exist.
        for query_file in (
            filename
            for filename in os.listdir(self.queries_dir)
            if filename.endswith(".json")
        ):
            name = os.path.splitext(query_file)[0]
            query_data_dir = os.path.join(self.data_dir, name)
            logging.debug("Creating query data directory: %s", query_data_dir)
            os.makedirs(query_data_dir, exist_ok=True)

    def scan_query_data(self, query_name: str) -> Dict[str, int]:
        """
        Get the list of local PDB files in the data directory for a given query.
        """
        query_data_dir = os.path.join(self.data_dir, query_name)
        ret = {}
        t_start = time.time()
        for filename in sorted(os.listdir(query_data_dir)):
            # Report hidden files if found, suggesting the command to remove them.
            filepath = os.path.join(query_data_dir, filename)
            if filename.startswith("."):
                logging.warning("Found hidden file: %s", filepath)
                print(f"rm {os.path.join(query_data_dir, filename)}")
                continue
            if filename.endswith(PDB_EXT) or filename.endswith(COMPRESSED_EXT):
                ret[download.filename_to_pdb_id(filename)] = os.path.getsize(filepath)
        # logging.debug(
        #     f"{query_name:<30}: {len(ret):>7,} local files in {time.time() - t_start:.2f} seconds."
        # )
        # log the same but using %s to avoid the formatting if the log level is not DEBUG.
        logging.debug(
            "%s: %7d local files scanned in %.2f seconds",
            query_name,
            len(ret),
            time.time() - t_start,
        )
        return ret

    def fetch_or_cache_query(self, query_path: str) -> List[str]:
        """
        Fetch the RCSB IDs from the RCSB website.

        :return: List of RCSB IDs.
        """
        # Get the list of PDB IDs from the RCSB website, given an advanced query in json format.
        return rcsbids.search_and_download_ids(query_path)

    def get_status_query(self, query_path: str) -> DirStatus:
        """
        Check the remote server for updates for a query and compute the status.

            - fetch the RCSB IDs from the RCSB website;
            - check which PDB files are already in the local project directory;
            - check which downloaded PDB files have zero size (i.e. they were not found on the server);
            - check which PDB files are obsolete;

        :param query_path: path to the query file.
        :return: a DirStatus object.
        """
        query_name = os.path.splitext(os.path.basename(query_path))[0]
        # Get the list of PDB IDs from the RCSB website.
        remote_ids = self.fetch_or_cache_query(query_path)
        # logging.debug(f"{query_name:<30}: {len(remote_ids):>7,} remote IDs.")
        # Log the same but using %s to avoid the formatting if the log level is not DEBUG.
        logging.debug("%s: %7d remote IDs", query_name, len(remote_ids))
        # Check which PDB files are already in the local project directory, and skip those to save time.
        local_ids = self.scan_query_data(query_name)
        n_local = len(local_ids)
        # Zero size files
        zero_ids = [local_id for local_id, size in local_ids.items() if size == 0]
        n_remote = len(remote_ids)

        # Remote structures to be downloaded.
        tbd_ids = [id_ for id_ in remote_ids if id_ not in local_ids]
        logging.info(
            "%s: %7d local, %7d remote, %7d to download",
            query_name,
            n_local,
            n_remote,
            len(tbd_ids),
        )
        # Local files to be removed (some local PDB files are not in the RCSB database anymore,
        # so we mark them with the SUFFIX_REMOVED suffix).
        removed_ids = [id_ for id_ in local_ids if id_ not in remote_ids]

        # Report the removed files.
        if removed_ids:
            # logging.info(
            #     f"Locally found {len(removed_ids):,} files not returned by RCSB for {query_name}.")
            logging.info(
                "Locally found %d files not returned by RCSB for %s",
                len(removed_ids),
                query_name,
            )
            for id_ in removed_ids:
                # logging.info(f"old_id='{id_}', query='{query_name}'")
                # log the same but using %s to avoid the formatting if the log level is not INFO.
                logging.info("old_id='%s', query='%s'", id_, query_name)

        return DirStatus(n_local, n_remote, tbd_ids, removed_ids, zero_ids)

    def get_status(self) -> ProjectStatus:
        """
        Fetch ids for each query and report the sync status of the project.

        :return: ProjectStatus, a dictionary mapping query names to DirStatus objects.
        """
        ret = {}
        for query_file in (
            filename
            for filename in sorted(os.listdir(self.queries_dir))
            if filename.endswith(".json")
        ):
            name = os.path.splitext(query_file)[0]
            query_path = os.path.join(self.queries_dir, query_file)
            ret[name] = self.get_status_query(query_path)
        return ret

    def mark_removed(self, query_name: str, to_remove: List[str]) -> None:
        """
        Mark obsolete the local PDB files that are not in the remote database anymore.

        :param query_name: name of the query.
        :param to_remove: list of PDB IDs to remove.
        """
        query_data_dir = os.path.join(self.data_dir, query_name)
        for id_ in to_remove:
            pdb_file = os.path.join(query_data_dir, download.pdb_id_to_filename(id_))
            # Problem: the file may be compressed.
            if not os.path.isfile(pdb_file):
                pdb_file += ".gz"
                assert os.path.isfile(
                    pdb_file
                ), f"File {pdb_file[:-3]} or {pdb_file} not found."
            logging.info("Marking %s as removed from RCSB.", pdb_file)
            os.rename(pdb_file, pdb_file + SUFFIX_REMOVED)

    def do_sync(
        self, project_status: ProjectStatus, n_jobs: int, compressed: bool = False
    ) -> None:
        """
        Synchronize the local directory with the remote repository.

        :param project_status: a dictionary mapping query names to DirStatus objects.
        :param n_jobs: number of parallel jobs to download the PDB files.
        """
        logging.info("Starting synchronization.")
        for query_name, dir_status in project_status.items():
            self.mark_removed(query_name, dir_status.removed_ids)
            query_data_dir = os.path.join(self.data_dir, query_name)
            download.download(
                dir_status.tbd_ids, query_data_dir, compressed=compressed, n_jobs=n_jobs
            )


def main(
    project_dir: str, n_jobs: int = 1, yes: bool = False, compressed: bool = False
):
    """
    Fetch the RCSB IDs from the RCSB website, and download the corresponding PDB files.

    :param project_dir: path to the project directory.
    :param n_jobs: number of parallel jobs to use.
    :param yes: if True, do not ask for confirmation before downloading the PDB files.
    """
    project = Project(project_dir)
    logging.info("Project directory: %s", project_dir)

    # Fetch the remote RCSB IDs.
    project_status = project.get_status()

    # Print the status of the project.
    print(project_dir)
    print(f"Date: {str(datetime.date.today())}")
    print(pformat_status(project_status))
    print()

    # Count the total number of files to be downloaded.
    total_tbd_ids = sum(
        len(dir_status.tbd_ids) for dir_status in project_status.values()
    )
    logging.info("📥 Total new files to be downloaded: %d", total_tbd_ids)

    # Download the PDB files corresponding to the RCSB PDB IDs which are not already in the project directory.
    if total_tbd_ids:
        if not yes:
            answer = input("Do you want to download the PDB files? [y/N] ")
            if answer.lower() != "y":
                logging.info("User chose not to download the PDB files.")
                return

        project.do_sync(project_status, n_jobs=n_jobs, compressed=compressed)


if __name__ == "__main__":
    # parse command line arguments
    parser = argparse.ArgumentParser(
        description="Download PDB files from the RCSB website."
    )
    parser.add_argument("project_dir", help="the directory of the project")
    parser.add_argument(
        "-j",
        "--n_jobs",
        type=int,
        default=DEFAULT_JOBS,
        help=f"the number of parallel jobs for downloading (default: {DEFAULT_JOBS}, max: {MAX_JOBS})",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="do not ask for confirmation before downloading",
    )
    parser.add_argument(
        "--compressed",
        action="store_true",
        help="download compressed PDB files (not available for AlphaFold DB)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose mode")
    args = parser.parse_args()

    # Configure logging
    # (see https://docs.python.org/3/howto/logging-cookbook.html#logging-to-multiple-destinations)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(name)s | %(levelname)-8s | %(message)s",
        # datefmt="%Y-%m-%d %H:%M:%S",  # no milliseconds
        filename=os.path.join(args.project_dir, "rcsb-sync.log"),
        filemode="a",
    )
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    # set a format which is simpler for console use
    console_formatter = logging.Formatter("%(name)-12s: %(levelname)-8s %(message)s")
    # tell the handler to use this format
    console.setFormatter(console_formatter)
    # add the handler to the root logger
    logging.getLogger("").addHandler(console)

    # Verbosity level for the logger (0: INFO, 1: DEBUG).
    console.setLevel(logging.DEBUG if args.verbose else logging.INFO)

    logging.info("Starting script: %s", __file__)
    # Log the command line arguments.
    logging.debug("Command line arguments: %s", args)
    main(args.project_dir, args.n_jobs, args.yes, args.compressed)
