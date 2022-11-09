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
import os
from collections import namedtuple
from typing import Dict
from typing import List

# My stuff
import download
import rcsbids

IDS_SEPARATOR = "\n"
SUFFIX_REMOVED = ".obsolete"
PDB_EXT = ".pdb.gz"

# Settings for the parallel download.
DEFAULT_JOBS = 1
MAX_JOBS = os.cpu_count()


# Named tuple to store the fetch results.
Diff = namedtuple("Diff", ["tbd_ids", "removed_ids"])
DataMap = Dict[str, List[str]]


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
            print("Creating directory:", self.data_dir)
            os.mkdir(self.data_dir)

        # Create the query data directories if they don't exist.
        for query_file in (
            filename
            for filename in os.listdir(self.queries_dir)
            if filename.endswith(".json")
        ):
            name = os.path.splitext(query_file)[0]
            query_data_dir = os.path.join(self.data_dir, name)
            os.makedirs(query_data_dir, exist_ok=True)

    def get_data_files_for_query(self, query_name: str) -> List[str]:
        """
        Get the list of PDB files in the query data directory.
        """
        query_data_dir = os.path.join(self.data_dir, query_name)
        return [
            filename
            for filename in os.listdir(query_data_dir)
            if filename.endswith(PDB_EXT)
        ]

    def get_local_query_ids(self, query_name) -> set:
        """
        Get the PDB IDs that are already in the project directory.
        """
        return {filename[:-7] for filename in self.get_data_files_for_query(query_name)}

    def fetch_or_cache_query(self, query_path: str) -> List[str]:
        """
        Fetch the RCSB IDs from the RCSB website.

        :return: List of RCSB IDs.
        """
        # Get the list of PDB IDs from the RCSB website, given an advanced query in json format.
        return rcsbids.search_and_download_ids(query_path)

    def updiff_query(self, query_path: str) -> Diff:
        """
        Check the remote server for updates for a query and compute the diff, but do not download the files.

            - fetch the RCSB IDs from the RCSB website;
            - check which PDB files are already in the local project directory;
            - check which PDB files are obsolete and mark them with the suffix '.obsolete';
            - print a sync report.

        :param query_path: path to the query file.
        """
        query_name = os.path.splitext(os.path.basename(query_path))[0]
        # Get the list of PDB IDs from the RCSB website.
        remote_ids = self.fetch_or_cache_query(query_path)
        # Check which PDB files are already in the local project directory, and skip those to save time.
        local_ids = self.get_local_query_ids(query_name)
        print("Local IDs:", len(local_ids))
        print("Remote IDs:", len(remote_ids))

        # Remote structures to be downloaded.
        tbd_ids = [id_ for id_ in remote_ids if id_ not in local_ids]
        # Local files to be removed (some local PDB files are not in the RCSB database anymore,
        # so we mark them with the SUFFIX_REMOVED suffix).
        removed_ids = [id_ for id_ in local_ids if id_ not in remote_ids]

        return Diff(tbd_ids, removed_ids)

    def updiff(self) -> Dict[str, Diff]:
        """
        Fetch ids for each query and report the difference with the local data.

        :return: a dictionary mapping query names to Diff objects.
        """
        ret = {}
        for query_file in (
            filename
            for filename in sorted(os.listdir(self.queries_dir))
            if filename.endswith(".json")
        ):
            name = os.path.splitext(query_file)[0]
            query_path = os.path.join(self.queries_dir, query_file)
            print(f"Query: {name}")
            ret[name] = self.updiff_query(query_path)
            print("ret[name].tbd_ids", ret[name].tbd_ids)
        return ret

    def mark_removed(self, query_name: str, to_remove: List[str]) -> None:
        """
        Mark obsolete the local PDB files that are not in the remote database anymore.

        :param query_name: name of the query.
        :param to_remove: list of PDB IDs to remove.
        """
        query_data_dir = os.path.join(self.data_dir, query_name)
        for id_ in to_remove:
            pdb_file = os.path.join(query_data_dir, id_ + PDB_EXT)
            assert os.path.isfile(pdb_file), f"File {pdb_file} not found."
            print("Marking obsolete:", pdb_file, "->", pdb_file + SUFFIX_REMOVED)
            os.rename(pdb_file, pdb_file + SUFFIX_REMOVED)

    def do_sync(self, diffs: Dict[str, Diff], n_jobs: int) -> None:
        """
        Synchronize the local directory with the remote repository.

        :param diffs: a dictionary mapping query names to Diff objects.
        :param n_jobs: number of parallel jobs to download the PDB files.
        """
        for query_name, diff in diffs.items():
            print(f"Syncing query {query_name}...")
            self.mark_removed(query_name, diff.removed_ids)
            query_data_dir = os.path.join(self.data_dir, query_name)
            download.download(
                diff.tbd_ids, query_data_dir, compressed=True, n_jobs=n_jobs
            )


def main(project_dir: str, n_jobs: int = 1, yes: bool = False) -> None:
    """
    Fetch the RCSB IDs from the RCSB website, and download the corresponding PDB files.

    :param project_dir: path to the project directory.
    :param n_jobs: number of parallel jobs to use.
    :param yes: if True, do not ask for confirmation before downloading the PDB files.
    """
    project = Project(project_dir)

    # Fetch the remote RCSB IDs.
    diffs = project.updiff()

    # Report the differences.
    for query_name, diff in diffs.items():
        print(f"Query: {query_name}")
        print(f"New files (remote but not local): {len(diff.tbd_ids):,}")
        print(f"Obsolete files (local but not remote): {len(diff.removed_ids):,}")

    # Count the total number of files to be downloaded.
    total_tbd_ids = sum(len(diff.tbd_ids) for diff in diffs.values())
    print(f"📥 Total new files to be downloaded: {total_tbd_ids:,}")

    # Download the PDB files corresponding to the RCSB PDB IDs which are not already in the project directory.
    if total_tbd_ids:
        if not yes:
            answer = input("Do you want to download the PDB files? [y/N] ")
            if answer.lower() != "y":
                print("Aborting.")
                return

        project.do_sync(diffs, n_jobs=n_jobs)


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
    args = parser.parse_args()
    main(args.project_dir, args.n_jobs, args.yes)
