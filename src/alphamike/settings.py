from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    mustang_path: Path = Path("MUSTANG_v3.2.3")
    ftp_server_host_domain_boundaries: str = "orengoftp.biochem.ucl.ac.uk"
    ftp_server_port_domain_boundaries: int = 21
    ftp_server_path_domain_boundaries: str = "cath/releases/all-releases/v4_1_0/cath-classification-data"
    ftp_server_filename_domain_boundaries: str = "cath-domain-boundaries-v4_1_0.txt"
    rcsb_server_download_root: HttpUrl = "https://files.rcsb.org/download/"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()