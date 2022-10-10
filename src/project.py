"""
Download protein structures for a project from the RCSB PDB database.

Usage
~~~~~

::

    python project.py project_dir [--n_jobs n_jobs]

Algorithm
~~~~~~~~~

0. If the ids are already downloaded (a ``_ids_<date>.txt`` cache file with current date exists), skip to step 2.
1. Start by downloading the RCSB PDB IDs for the project, using the queries in the ``queries`` directory.
2. Before downloading the PDB files, check which PDB files are already in the local project directory,
   and skip those to save time.
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
    ├── Project
    │   ├── _ids_2022-01-01.txt
    │   ├── _ids_2022-03-01.txt
    │   ├── queries
    │   │   ├── query_0.json
    │   │   ├── query_1.json
    │   │   └── query_2.json
    │   └── data
    │       ├── 1i5r.pdb.gz
    │       ├── 1k8o.pdb.gz
    │       .
    │       .
    │       .
    │       └── 1q9s.pdb.gz
    ...
"""
# Standard Library
import argparse
import datetime
import os
import time
from collections import namedtuple
from typing import List

# My stuff
from download import download
from rcsbids import load_pdb_ids
from rcsbids import search_and_download_ids
from rcsbids import store_pdb_ids

IDS_SEPARATOR = '\n'
SUFFIX_REMOVED = '.obsolete'
PDB_EXT = '.pdb.gz'

# Settings for the parallel download.
DEFAULT_JOBS = 1
MAX_JOBS = os.cpu_count()


# Named tuple to store the fetch results.
FetchResult = namedtuple('FetchResult', ['tbd_ids', 'removed_ids'])


class Project:
    """
    Keep synced the data directory with the remote RCSB database.
    """

    def __init__(self, directory: str, verbose: bool = False):
        self.directory = directory
        self.queries_dir = os.path.join(self.directory, 'queries')
        self.data_dir = os.path.join(self.directory, 'data')
        self.verbose = verbose

        # Create the data directory if it does not exist.
        if not os.path.isdir(self.data_dir):
            print('Creating directory:', self.data_dir)
            os.mkdir(self.data_dir)

        # List of all the remote RCSB IDs.
        self.remote_pdb_ids: List[str] = []
        # List of all the remote RCSB IDs that are not in the local directory.
        self.tbd_pdb_ids: List[str] = []
        # List of all the IDs that are in the local directory but are not in the remote database anymore.
        self.obsolete_pdb_ids: List[str] = []

    def _get_cache_file(self) -> str:
        """
        Get the path to the pdb ids cache file.
        """
        return os.path.join(self.directory, '_ids_' + datetime.date.today().isoformat() + '.txt')

    def get_local_ids(self) -> set:
        """
        Get the PDB IDs that are already in the project directory.
        """
        local_ids = set()
        for filename in os.listdir(self.data_dir):
            if filename.endswith('pdb.gz'):
                local_ids.add(filename[:-7])
        return local_ids

    def fetch_remote_ids(self, cache_file: str) -> List[str]:
        """
        Fetch the RCSB IDs from the RCSB website.

        :param cache_file: path to the file where the list of RCSB IDs will be saved.
        :return: list of RCSB IDs.
        """
        remote_ids = []
        for query_file in os.listdir(self.queries_dir):
            if not query_file.endswith('.json'):
                continue
            query = os.path.join(self.queries_dir, query_file)
            remote_ids += search_and_download_ids(query)

        # Cache the ids.
        store_pdb_ids(remote_ids, cache_file)

        return remote_ids

    def fetch_or_cache(self) -> List[str]:
        """
        Fetch the RCSB IDs from the RCSB website, or use the cached IDs if they exist.

        Side effect:
            - the remote RCSB IDs are saved in the project directory, in a file named ``_ids_<date>.txt``
              (where <date> is the current date).

        :return: List of RCSB IDs.
        """
        # Check if the ids are already downloaded. If so, read them from the _ids_<date>.txt file.
        ids_cache_file = self._get_cache_file()
        if os.path.isfile(ids_cache_file):
            # Read the ids from the _ids_<date>.txt file.
            remote_ids = load_pdb_ids(ids_cache_file)
        else:
            # Get the list of PDB IDs from the RCSB website, given an advanced query in json format.
            if self.verbose:
                print('Fetching remote IDs...')
            remote_ids = self.fetch_remote_ids(ids_cache_file)
        return remote_ids

    def fetch(self) -> FetchResult:
        """
        Similarly to git fetch, check for updates, update "indexes", but do not download the files.

            - fetch the RCSB IDs from the RCSB website;
            - check which PDB files are already in the local project directory;
            - check which PDB files are obsolete and mark them with the suffix '.obsolete';
            - print a sync report.
        """
        remote_ids = self.fetch_or_cache()

        # Check which PDB files are already in the local project directory, and skip those to save time.
        local_ids = self.get_local_ids()
        # Files to be downloaded.
        tbd_ids = [id_ for id_ in remote_ids if id_ not in local_ids]
        # Some local PDB files are not in the RCSB database anymore, so we mark them with the SUFFIX_REMOVED suffix.
        print('Local IDs:', len(local_ids))
        print('Remote IDs:', len(remote_ids))
        removed_ids = [id_ for id_ in local_ids if id_ not in remote_ids]
        # Now we can calculate the number of files already downloaded.
        n_downloaded_ok = len(local_ids) - len(removed_ids)

        # Print a numeric report of:
        # - the number of all remote PDB files (in the RCSB database) related to the queries;
        # - the number of remote files already in the local project directory;
        # - the number of PDB files that are in the remote database and not in the local project directory;
        # - the number of removed/obsolete PDB files (i.e. those that are not in the remote database anymore).
        if tbd_ids:
            completion_rate = round(100 * n_downloaded_ok / len(remote_ids), 3)
            print(f'{n_downloaded_ok}/{len(remote_ids)} ({completion_rate}%)')
        else:
            if self.verbose:
                print(f'🦜 Up to date ({len(remote_ids):,} structures).')

        if removed_ids:
            # Print the list of removed/obsolete PDB files.
            print('\n'.join(removed_ids))
            print(f'🗑 Obsolete files (local but not remote): {len(removed_ids):,}')

        self.remote_pdb_ids = remote_ids
        self.tbd_pdb_ids = tbd_ids
        self.obsolete_pdb_ids = removed_ids

        # return tbd_ids, removed_ids in a namedtuple
        return FetchResult(tbd_ids, removed_ids)

    def mark_obsolete(self) -> None:
        """
        Mark obsolete the local PDB files that are not in the remote database anymore.
        """
        for id_ in self.obsolete_pdb_ids:
            pdb_file = os.path.join(self.data_dir, id_ + PDB_EXT)
            if os.path.isfile(pdb_file):
                print('Marking obsolete:', pdb_file, '->', pdb_file + SUFFIX_REMOVED)
                os.rename(pdb_file, pdb_file + SUFFIX_REMOVED)

    def pull(self, n_jobs: int) -> None:
        """
        Similarly to git pull, synchronize the local working directory with the remote repository.

            - download the PDB files corresponding to the RCSB PDB IDs which are not already in the project directory.
            - every 10 downloaded files, report the global progress and the expected time to complete
              (based on the number of PDB files to be downloaded).

        :param n_jobs: number of parallel jobs to download the PDB files.
        """
        if not self.remote_pdb_ids:
            # If the remote RCSB IDs have not been fetched yet, fetch them.
            tbd_ids, _ = self.fetch()

        # Download the PDB files corresponding to the RCSB PDB IDs which are not already in the project directory.
        total_tbd_ids = len(tbd_ids)

        print('Downloading RCSB PDB files...')
        start_time = time.time()
        try:
            download(tbd_ids, self.data_dir, compressed=True, n_jobs=n_jobs)
        except KeyboardInterrupt:
            print('\nDownload interrupted by user.')
        else:
            elapsed_time = time.time() - start_time
            print(f'\nDownloaded {total_tbd_ids} files in {elapsed_time:.2f} seconds', end=' ')
            print(f'({elapsed_time / total_tbd_ids:.2f} seconds per file).')

        # Now refetch the local PDB IDs, to check if the files have been downloaded correctly.
        self.fetch()


def main(project_dir: str, n_jobs: int = 1, verbose: bool = False) -> None:
    """
    Fetch the RCSB IDs from the RCSB website, and download the corresponding PDB files.

    :param project_dir: path to the project directory.
    :param n_jobs: number of parallel jobs to use.
    :param verbose: quite quiet if False.
    """
    project = Project(project_dir, verbose=verbose)

    # Fetch the remote RCSB IDs.
    tbd_ids, removed_ids = project.fetch()

    # Mark obsolete the local PDB files that are not in the remote database anymore.
    if (
        removed_ids
        and input(f'\nMark {len(removed_ids)} PDB files as obsolete? (y/n) ') == 'y'
    ):
        project.mark_obsolete()

    # Ask the user to confirm the download of missing PDB files.
    if len(tbd_ids) > 0:
        answer = input(f'\nDo you want to download {len(tbd_ids)} PDB files? (y/n) ')
        if answer.lower() == 'y':
            project.pull(n_jobs=n_jobs)
        else:
            print('Download cancelled.')


if __name__ == '__main__':
    # parse command line arguments
    parser = argparse.ArgumentParser(description='Download PDB files from the RCSB website.')
    parser.add_argument('project_dir', help='the directory of the project')
    parser.add_argument('-j', '--n_jobs', type=int, default=DEFAULT_JOBS,
                        help=f'the number of parallel jobs for downloading (default: {DEFAULT_JOBS}, max: {MAX_JOBS})')
    parser.add_argument('-v', '--verbose', action='store_true', help='print verbose output')
    args = parser.parse_args()

    main(args.project_dir, args.n_jobs, args.verbose)
