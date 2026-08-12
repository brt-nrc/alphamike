import requests
import logging
from ftplib import FTP
from pathlib import Path
from alphamike.settings import settings

logger: logging.Logger = logging.getLogger(__name__)

class DownloadError(Exception):
    pass


class FileError(Exception):
    pass


class DownloadClient:
    """Handles downloading files from FTP and HTTP servers."""

    def __init__(self):
        pass

    @staticmethod
    def download_list_ftp(destination_file_path: Path) -> Path:
        """Downloads domain boundaries text file."""
        logger.debug(f"Downloading domain boundaries file.")
        filename: str = settings.ftp_server_filename_domain_boundaries
        try:
            with FTP(settings.ftp_server_host_domain_boundaries) as ftp:      # Open FTP connection
                ftp.login()                                                   # Anonymous login
                ftp.cwd(settings.ftp_server_path_domain_boundaries)
                with open(destination_file_path, 'wb') as fp:
                    ftp.retrbinary('RETR '+filename, fp.write)
        except Exception as err:
            raise DownloadError(f"Error occurred while downloading domain boundaries file: {err}")
        return destination_file_path

    @staticmethod
    def download_pdb(pdb_name: str, destination_folder_path: Path) -> Path:
        """Downloads .pdb files from rcsb.org"""
        logger.debug(f"Downloading PDB file: {pdb_name}")

        download_folder: Path = destination_folder_path / "source"
        download_folder.mkdir(parents=True, exist_ok=True)
        download_filepath: Path = download_folder / pdb_name

        with requests.get(str(settings.rcsb_server_download_root) + pdb_name, stream=True) as r:
            if not r.status_code == 200:
                raise DownloadError(r.status_code)
            try:
                with open(download_filepath, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            except Exception as err:
                raise FileError('Download save failed', err)
        return download_filepath