import logging
from pathlib import Path
from alphamike.settings import settings
from alphamike.download_client import DownloadClient

logger: logging.Logger = logging.getLogger(__name__)

class CreationError(Exception):
    pass

class DownloadError(Exception):
    pass

def create_domain(domain: str, folder_path: Path = Path('pdb')) -> Path:
    """Creates a domain PDB file from the main PDB file and the domain boundaries file.
    If the PDB file already exists in the folder_path, it will not be downloaded again.
    
    :params str domain: The domain name to create.
    :params Path folder_path: The path to the folder where the domain PDB file will be created.
    :raises ValueError: If the domain name is not 7 characters long.
    :raises CreationError: If there is an error creating the domain PDB file.
    """
    pdb_ext = '.pdb'
    domain_protein: str = domain[0:5]
    domain_protein_chain: str = domain[4]
    domain_number_in_chain: str = domain[-2:]
    domain_boundaries_file = Path(settings.ftp_server_filename_domain_boundaries)
    if domain_boundaries_file.is_file() is False:
        logger.info(f"Domain boundaries file not found. Downloading from FTP server.")
        DownloadClient.download_list_ftp(domain_boundaries_file)
    else:
        logger.debug(f"Domain boundaries file found. Using existing file.")

    folder_path.mkdir(exist_ok=True)
    pdb_domain_file = domain + pdb_ext
    pdb_domain_path = folder_path / pdb_domain_file
    if not len(domain) == 7:
        raise ValueError('Create Domain Name input wrong')
    if not pdb_domain_path.is_file():
        logger.debug(f'Making {domain} domain')
        domain_range = []
        domain_boundaries = []
        # See if the raw PDB file has already been downloaded
        pdb_main_path = folder_path / 'source'
        pdb_main_file = domain[0:4] + pdb_ext
        pdb_main = pdb_main_path / pdb_main_file
        if not pdb_main.is_file():
            try:
                DownloadClient.download_pdb(pdb_main_file, folder_path)
            except Exception as err:
                logger.error(f"Error occurred while downloading PDB file: {err}")
                raise DownloadError("Error occurred while downloading PDB file", err)
        # From the main PDB file, we need to extract the domain boundaries from the domain boundaries file and create a new PDB file for the domain.
        with open(domain_boundaries_file) as file:
            for line_content in file:
                line = line_content.split()
                if line[0] == domain_protein:
                    index_sum = 3
                    if not int(domain_number_in_chain) == 0: 
                        for i in range(int(domain_number_in_chain)-1):
                            d = int(line[index_sum])
                            index_sum += d * 6 + 1
                    index_max = index_sum + int(line[index_sum])*6
                    if domain_protein_chain.isdigit():
                        domain_boundaries = [e for e in line[index_sum:index_max] if not e == '-' or e.isalpha()]
                        domain_boundaries = [int(e) for e in domain_boundaries[::2]]
                    elif domain_protein_chain.isalpha():
                        domain_boundaries = [int(e) for e in line[index_sum:index_max] if not (e == '-' or e.isalpha())]
                    for i in range(domain_boundaries[0]):
                        domain_range.extend(range(domain_boundaries[1 + i * 2], domain_boundaries[2 + i * 2]+1))
            with open(pdb_main) as pdbfile:
                try:
                    with open(pdb_domain_path, "w") as domainfile:
                        for pdbline in pdbfile:
                            pdblinelist = pdbline.split()
                            if pdblinelist[0] == 'ATOM':
                                pdbnumber = pdblinelist[5]
                                chainletter = pdblinelist[4]
                                if pdbnumber[-1].isalpha():
                                    pdbnumber = pdbnumber[:-1]
                                if len(pdblinelist[4]) == 5:
                                    pdbnumber = pdblinelist[4][1:]
                                    chainletter = pdblinelist[4][0]
                                if (chainletter == domain[4]) and (int(pdbnumber) in domain_range):
                                    print(pdbline, file=domainfile, end='')
                except Exception as err:
                    logger.error(f"Error occurred while creating domain file: {err}")
                    raise CreationError("domain file error", err)
    return pdb_domain_path