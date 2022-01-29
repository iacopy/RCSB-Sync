"""
Download protein structures for an organism from the RCSB PDB database.

Usage
~~~~~

    python organism.py --organism_dir organism_dir [--n_jobs n_jobs]

Algorithm
~~~~~~~~~

0. If the ids are already downloaded (a ``_ids_<date>.txt`` file with current date exists), skip to the next step.
1. Start by downloading the RCSB PDB IDs for the organism, using the queries in the ``queries`` directory.
2. Before downloading the PDB files, check which PDB files are already in the local organism directory,
   and skip those to save time.
3. Some local PDB files are not in the RCSB database anymore, so we mark them with a suffix (for example '.removed').
4. Print a numeric report of:
   - the number of PDB files already in the organism directory;
   - the number of PDB files that will be downloaded;
   - the number of removed/obsolete PDB files.

5. Download the PDB files corresponding to the RCSB PDB IDs which are not already in the organism directory.
6. During the download, report the global progress and the expected time to completion.

Directory structure
~~~~~~~~~~~~~~~~~~~

The directory structures of organisms are as follows::

    .
    ├── Organism
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
from typing import List, Set

# My stuff
from download import download
from rcsbids import search_and_download_ids

IDS_SEPARATOR = '\n'
SUFFIX_REMOVED = '.obsolete'

# Settings for the parallel download.
DEFAULT_JOBS = 2
MAX_JOBS = os.cpu_count()


class Organism:
    """
    Keep synced the data directory with the remote RCSB database.
    """

    def __init__(self, directory: str) -> None:
        self.directory = directory
        self.queries_dir = os.path.join(self.directory, 'queries')
        self.data_dir = os.path.join(self.directory, 'data')
        # Create the data directory if it does not exist.
        if not os.path.isdir(self.data_dir):
            print('Creating directory:', self.data_dir)
            os.mkdir(self.data_dir)

        # Set of local RCSB IDs, which are already in the local directory (i.e. not to be downloaded).
        self.local_pdb_ids: Set[str] = set()
        # List of all the remote RCSB IDs.
        self.remote_pdb_ids: Set[str] = set()
        # List of all the remote RCSB IDs that are not in the local directory.
        self.tbd_pdb_ids: List[str] = []
        # List of all the IDs that are in the local directory but are not in the remote database anymore.
        self.obsolete_pdb_ids: List[str] = []

    def get_local_ids(self) -> set:
        """
        Get the PDB IDs that are already in the organism directory.
        """
        local_ids = set()
        for filename in os.listdir(self.data_dir):
            # if filename.endswith('.pdb'):
            #     local_ids.append(filename[:-4])
            if filename.endswith('pdb.gz'):
                local_ids.add(filename[:-7])
        return local_ids

    def fetch_remote_ids(self, cache_file: str) -> List[str]:
        """
        Fetch the RCSB IDs for the organism from the RCSB website.

        :return: List of RCSB IDs.
        """
        remote_ids = []
        for query_file in os.listdir(self.queries_dir):
            if not query_file.endswith('.json'):
                continue
            query = os.path.join(self.queries_dir, query_file)
            remote_ids += search_and_download_ids(query, cache_file)
        return remote_ids

    def fetch_or_cache(self) -> List[str]:
        """
        Fetch the RCSB IDs for the organism from the RCSB website, or use the cached IDs if they exist.

        Side effect:
            - the remote RCSB IDs are saved in the organism directory, in a file named ``_ids_<date>.txt``
              (where <date> is the current date).

        :return: List of RCSB IDs.
        """
        # Check if the ids are already downloaded. If so, read them from the _ids_<date>.txt file.
        ids_cache_file = os.path.join(self.directory, '_ids_' + datetime.date.today().isoformat() + '.txt')
        if os.path.isfile(ids_cache_file):
            print('Reading cached IDs from:', ids_cache_file)
            # Read the ids from the _ids_<date>.txt file.
            with open(ids_cache_file, 'r', encoding='ascii') as file_pointer:
                remote_ids = file_pointer.read().split(IDS_SEPARATOR)
        else:
            # Get the list of PDB IDs from the RCSB website, given an advanced query in json format.
            print('Fetching remote IDs...')
            remote_ids = self.fetch_remote_ids(ids_cache_file)
            # Save the list of PDB IDs to a file.
            with open(ids_cache_file, 'w', encoding='ascii') as file_pointer:
                file_pointer.write(IDS_SEPARATOR.join(remote_ids))
        return remote_ids

    def fetch(self) -> None:
        """
        Similar to ``git fetch``:
            - fetch the RCSB IDs for the organism from the RCSB website;
            - check which PDB files are already in the local organism directory;
            - check which PDB files are obsolete and mark them with the suffix '.removed';
        """
        remote_ids = set(self.fetch_or_cache())

        # Check which PDB files are already in the local organism directory, and skip those to save time.
        local_ids = self.get_local_ids()
        # Files to be downloaded.
        tbd_ids = [id_ for id_ in remote_ids if id_ not in local_ids]
        # Some local PDB files are not in the RCSB database anymore, so we mark them with the SUFFIX_REMOVED suffix.
        removed_ids = [id_ for id_ in local_ids if id_ not in remote_ids]
        # Now we can calculate the number of files already downloaded.
        n_downloaded_ok = len(local_ids) - len(removed_ids)

        # Print a numeric report of:
        # - the number of local PDB files of the organism;
        # - the number of all remote PDB files of the organism;
        # - the number of remote files already in the local organism directory;
        # - the number of PDB files that are in the remote database and not in the local organism directory;
        # - the number of removed/obsolete PDB files (i.e. those that are not in the remote database anymore).
        print('\n' + self.directory)
        if remote_ids:
            print('Total remote PDB files: ' + str(len(remote_ids)))
        if local_ids:
            print('Local PDB files: ' + str(len(local_ids)))
        if n_downloaded_ok:
            print('💾 Already downloaded PDB files: ' + str(n_downloaded_ok))
        if removed_ids:
            print('🗑 Files removed/obsolete: ' + str(len(removed_ids)))
        if tbd_ids:
            print('🌍 Files to be downloaded: ' + str(len(tbd_ids)))
        else:
            print('✅ Up to date.')

        self.remote_pdb_ids = remote_ids
        self.local_pdb_ids = local_ids
        self.tbd_pdb_ids = tbd_ids
        self.obsolete_pdb_ids = removed_ids

    def mark_obsolete(self) -> None:
        """
        Mark obsolete the local PDB files that are not in the remote database anymore.
        """
        for id_ in self.obsolete_pdb_ids:
            pdb_file = os.path.join(self.data_dir, id_ + '.pdb.gz')
            if os.path.isfile(pdb_file):
                print('Marking obsolete:', pdb_file, '->', pdb_file + SUFFIX_REMOVED)
                os.rename(pdb_file, pdb_file + SUFFIX_REMOVED)

    def pull(self, n_jobs: int) -> None:
        """
        Similar to ``git pull`` (synchronize the local and remote files):
            - download the PDB files corresponding to the RCSB PDB IDs which are not already in the organism directory.
            - every 10 downloaded files, report the global progress and the expected time to complete
              (based on the number of PDB files to be downloaded).
        """
        if not self.remote_pdb_ids:
            # If the remote RCSB IDs have not been fetched yet, fetch them.
            self.fetch()

        # Download the PDB files corresponding to the RCSB PDB IDs which are not already in the organism directory.
        tbd_ids = self.tbd_pdb_ids
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


def main(organism_dir: str, n_jobs: int = 1) -> None:
    """
    Fetch the RCSB IDs for the organism from the RCSB website, and download the corresponding PDB files.

    :param organism_dir: path to the organism directory.
    :param n_jobs: number of parallel jobs to use.
    """
    # TODO: less verbose output.

    # Create the organism object.
    organism = Organism(organism_dir)

    # Fetch the remote RCSB IDs.
    organism.fetch()

    # Mark obsolete the local PDB files that are not in the remote database anymore.
    if (
        organism.obsolete_pdb_ids
        and input(f'\nMark {len(organism.obsolete_pdb_ids)} PDB files as obsolete? (y/n) ') == 'y'
    ):
        organism.mark_obsolete()

    # Ask the user to confirm the download of missing PDB files.
    if len(organism.tbd_pdb_ids) > 0:
        answer = input(f'\nDo you want to download {len(organism.tbd_pdb_ids)} PDB files? (y/n) ')
        if answer.lower() == 'y':
            organism.pull(n_jobs=n_jobs)
        else:
            print('Download cancelled.')
    else:
        print('🍺 All PDB files are already in the organism directory.')


if __name__ == '__main__':
    # parse command line arguments
    parser = argparse.ArgumentParser(description='Download PDB files from the RCSB website.')
    parser.add_argument('organism_dir', help='the directory of the organism')
    parser.add_argument('-j', '--n_jobs', type=int, default=DEFAULT_JOBS,
                        help=f'the number of parallel jobs for downloading (default: {DEFAULT_JOBS}, max: {MAX_JOBS})')
    args = parser.parse_args()

    # Run the main function.
    main(args.organism_dir, args.n_jobs)
