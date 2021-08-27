from ftplib import FTP
import os
import requests
import csv

class FolderCreationError(Exception):
    pass


class DownloadError(Exception):
    pass


class InputError(Exception):
    pass


class FileError(Exception):
    pass


def download_list_ftp() -> None:
    """Downloads domain boundaries text file."""
    filename = 'cath-domain-boundaries-v4_1_0.txt'                              # Version 4.1.0
    with FTP('orengoftp.biochem.ucl.ac.uk') as ftp:                             # Open FTP connection
        ftp.login()                                                             # Anonymous login
        ftp.cwd('cath/releases/all-releases/v4_1_0/cath-classification-data')   # Change working directory
        with open(filename, 'wb') as fp:                                        # Open local file
            ftp.retrbinary('RETR '+filename, fp.write)                          # RETR remote file


def check_make_dir(path: 'path') -> None:
    """Checks if a folder exists and if it doesn't it creates it"""
    abspath = os.path.abspath(path)                                             # Get absolute path
    if not os.path.isdir(abspath):                                              # If the path is not a directory
        try:
            os.mkdir(abspath)                                                   # Make directory
        except Exception as err:
            raise FolderCreationError(err)


def download_pdb(name: str, folder_path: 'path' = 'pdb') -> None:
    """Downloads .pdb files from rcsb.org"""
    print("****DEBUG: download_pdb", name, sep='\t')
    baseurl = 'https://files.rcsb.org/download/'                                # Downloading files from rcsb.org
    abspath_tmp = os.path.abspath(folder_path)                                  # Create absolute path of folder_path
    check_make_dir(abspath_tmp)                                                 # Calls check_make_dir
    sources_path = os.path.join(abspath_tmp, 'source')                          # Creates folder_path/sources path
    check_make_dir(sources_path)                                                # Checks for pdb/sources dir for downloaded .pdb files
    filepath = os.path.join(sources_path, name)                                 # Creates downloaded .pdb file name
    with requests.get(baseurl + name, stream=True) as r:                        # Open file stream
        if not r.status_code == 200:                                            # Checks if request is successful
            raise DownloadError(r.status_code)
        try:
            with open(filepath, 'wb') as f:                                     # Opens local file
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)                                              # Writes file in chunks
        except Exception as err:
            raise FileError('Download save failed', err)


def initialize_csv(name: 'str' = 'results') -> None:
    """Initializes .csv files with headers"""
    filename = name + '.csv'
    try:                                                                        # Creates filename
        with open(filename, 'w') as file:                                        # Opens file
            titles = ['Barcode', 'Identities', 'Length', 'Percentage', 'Notes']          # Headers
            writer = csv.writer(file)
            writer.writerow(titles)                              # Writes comma-separated headers to file
    except Exception as err:
        raise Exception(err)
