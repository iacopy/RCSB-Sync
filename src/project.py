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
import csv
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
import rcsbquery

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


def status_to_table(project_status: ProjectStatus) -> list:
    """
    Convert the status of the project to a table.

    :param project_status: dictionary with the status of the project.
    :return: a list of lists with the table.
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
    # prepend the headers
    table.insert(
        0,
        [
            "Query",
            "Local",
            "Zero",
            "Valid",
            "Remote",
            "To download",
            "Removed",
        ],
    )
    return table


def pformat_status(project_status: ProjectStatus) -> str:  # pragma: no cover
    """
    Create a nice string table with the status of the project.

    :param project_status: dictionary with the status of the project.
    :return: a string with the table.
    """
    table = status_to_table(project_status)
    return tabulate(table, headers="firstrow", tablefmt="pipe")


def log_dir_status(dir_status: DirStatus, query_name: str):
    """
    Log the status of a directory.

    :param dir_status: the status of the directory.
    :param query_name: name of the query.
    """
    logging.debug(
        "📁 %s: %d local, %d remote, %d to be downloaded, %d removed",
        query_name,
        dir_status.n_local,
        dir_status.n_remote,
        len(dir_status.tbd_ids),
        len(dir_status.removed_ids),
    )
    if dir_status.tbd_ids:
        logging.info(
            "📥 %-30s:   new files: %7d",
            query_name,
            len(dir_status.tbd_ids),
        )
    if dir_status.removed_ids:
        logging.info(
            "🗑️ %-30s: local PDB not returned by RCSB: %7d",
            query_name,
            len(dir_status.removed_ids),
        )
        for id_ in dir_status.removed_ids:
            logging.info("old_id='%s', query='%s'", id_, query_name)


class ProjectInitError(Exception):
    """
    Error raised when the project cannot be initialized.
    """


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

        if not os.path.isdir(self.queries_dir):
            # search for a project.yml to generate the queries
            try:
                query_files = rcsbquery.prepare_queries(self.directory)
            except FileNotFoundError as exc:
                logging.error(
                    "No queries directory found in %s, and no project.yml file found.",
                    self.directory,
                )
                raise ProjectInitError(
                    f"No queries directory found in {self.directory}, and no project.yml file found."
                ) from exc
            logging.info("%d queries created", len(query_files))

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
        files = {}
        t_start = time.time()
        for filename in sorted(os.listdir(query_data_dir)):
            # Report hidden files if found, suggesting the command to remove them.
            filepath = os.path.join(query_data_dir, filename)
            if filename.startswith("."):
                logging.warning("Found hidden file: %s", filepath)
                print(f"rm {os.path.join(query_data_dir, filename)}")
                continue
            if filename.endswith(PDB_EXT) or filename.endswith(COMPRESSED_EXT):
                size = os.path.getsize(filepath)
                ret[download.filename_to_pdb_id(filename)] = size
                files[filename] = size
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

        # Store files in a csv file.
        print(f"Writing {query_name}__files.csv")
        files_file = os.path.join(self.data_dir, f"{query_name}__files.csv")
        with open(files_file, "w", encoding="ascii") as file:
            for filename in sorted(files):
                file.write(f"{filename}\n")
        return ret

    def fetch_or_cache_query(self, query_path: str) -> List[str]:
        """
        Fetch the RCSB IDs from the RCSB website.

        Side effect: create a file with the list of IDs in the data directory.

        :param query_path: path to the query file.
        :return: List of RCSB IDs.
        """
        # Get the list of PDB IDs from the RCSB website, given an advanced query in json format.
        ret = rcsbids.search_and_download_ids(query_path)

        # Side effect: store the list of PDB IDs in a file in the data directory.
        query_name = os.path.splitext(os.path.basename(query_path))[0]
        ids_file = os.path.join(self.data_dir, f"{query_name}.ids")
        with open(ids_file, "w", encoding="ascii") as file:
            file.write("\n".join(ret))

        # Also create a bash script to download the PDB files.
        download.ids_to_sh(ids_path=ids_file)

        return ret

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
        # Check which PDB files are already in the local project directory, and skip those to save time.
        local_ids = self.scan_query_data(query_name)
        n_local = len(local_ids)
        # Zero size files
        zero_ids = [local_id for local_id, size in local_ids.items() if size == 0]
        n_remote = len(remote_ids)

        # Remote structures to be downloaded.
        tbd_ids = [id_ for id_ in remote_ids if id_ not in local_ids]

        # Local files to be removed (some local PDB files are not in the RCSB database anymore,
        # so we mark them with the SUFFIX_REMOVED suffix).
        removed_ids = [id_ for id_ in local_ids if id_ not in remote_ids]
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
            if filename.endswith(".json") and not filename.startswith(".")
        ):
            name = os.path.splitext(query_file)[0]
            query_path = os.path.join(self.queries_dir, query_file)
            ret[name] = self.get_status_query(query_path)
            log_dir_status(ret[name], name)
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
        logging.debug("Starting synchronization.")
        for query_name, dir_status in project_status.items():
            self.mark_removed(query_name, dir_status.removed_ids)
            query_data_dir = os.path.join(self.data_dir, query_name)
            download.download(
                dir_status.tbd_ids, query_data_dir, compressed=compressed, n_jobs=n_jobs
            )


def main(
    project_dir: str,
    n_jobs: int = 1,
    yes: bool = False,
    noop: bool = False,
    compressed: bool = False,
    summary: bool = False,
):  # pylint: disable=too-many-arguments
    """
    Fetch the RCSB IDs from the RCSB website, and download the corresponding PDB files.

    :param project_dir: path to the project directory.
    :param n_jobs: number of parallel jobs to use.
    :param yes: if True, do not ask for confirmation before downloading the PDB files.
    :param noop: if True, do not download the PDB files.
    :param compressed: if True, download the compressed PDB files (.gz). Don't work with AlphaFold.
    """
    project = Project(project_dir)
    logging.debug("Project directory: %s", project_dir)

    # Fetch the remote RCSB IDs.
    project_status = project.get_status()

    # Print the status of the project.
    if summary:  # pragma: no cover
        print(project_dir)
        print(f"Date: {str(datetime.date.today())}")
        print(pformat_status(project_status))

    # store a csv file with the status
    table = status_to_table(project_status)
    # export the list of lists to a csv file
    with open(
        os.path.join(project_dir, "db_summary.csv"), "w", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerows(table)

    # Also store the status in txt format.
    with open(
        os.path.join(project_dir, "db_summary.txt"), "w", encoding="utf-8"
    ) as file:
        file.write(pformat_status(project_status))

    # Count the total number of files to be downloaded.
    total_tbd_ids = sum(
        len(dir_status.tbd_ids) for dir_status in project_status.values()
    )
    if total_tbd_ids == 0:
        logging.debug("Nothing to do.")
        return

    logging.info("📥 Number of new pdb files to download overall: %7d", total_tbd_ids)

    # If "--noop" argument is given, exit.
    if noop:
        logging.debug("Exiting because of --noop argument.")
        return

    # Download the PDB files corresponding to the RCSB PDB IDs which are not already in the project directory.
    if not yes:
        answer = input(
            f"\nDo you want to download the {total_tbd_ids} PDB files? [y/N] "
        )
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
    yes_or_no = parser.add_mutually_exclusive_group()
    yes_or_no.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="do not ask for confirmation before downloading",
    )
    yes_or_no.add_argument(
        "-n",
        "--noop",
        action="store_true",
        help="do not download new files if available",
    )
    parser.add_argument(
        "--compressed",
        action="store_true",
        help="download compressed PDB files (not available for AlphaFold DB)",
    )
    # Add an option to print the database summary table
    parser.add_argument(
        "-s", "--summary", action="store_true", help="print the database summary table"
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
    console_formatter = logging.Formatter("%(levelname)-8s %(message)s")
    # tell the handler to use this format
    console.setFormatter(console_formatter)
    # add the handler to the root logger
    logging.getLogger("").addHandler(console)

    # Verbosity level for the logger (0: INFO, 1: DEBUG).
    console.setLevel(logging.DEBUG if args.verbose else logging.INFO)

    logging.debug("Starting script: %s", __file__)
    # Log the command line arguments.
    logging.debug("Command line arguments: %s", args)
    main(
        args.project_dir,
        args.n_jobs,
        args.yes,
        args.noop,
        args.compressed,
        args.summary,
    )
