
from pathlib import Path
import pytest
from unittest.mock import patch
from alphamike.download_client import DownloadClient, DownloadError, FileError

@pytest.fixture
def mock_dependencies(tmp_path):
    with patch("alphamike.download_client.FTP") as mock_ftp, \
         patch("alphamike.download_client.settings") as mock_settings, \
         patch("alphamike.download_client.requests.get") as mock_get:
        
        mock_ftp_instance = mock_ftp.return_value.__enter__.return_value
        mock_settings.ftp_server_domain_boundaries = "localhost"
        
        mock_settings.ftp_server_host_domain_boundaries = "localhost"
        mock_settings.ftp_server_path_domain_boundaries = "/test/path"
        mock_settings.ftp_server_filename_domain_boundaries = "test_boundaries.txt"

        # mock_response represents the 'r' in 'with requests.get(...) as r:'
        mock_response = mock_get.return_value.__enter__.return_value
        
        # Set up a default successful response
        mock_response.status_code = 200
        
        # iter_content should yield a list of byte chunks
        mock_response.iter_content.return_value = [b"test ", b"file ", b"content"]
        
        yield mock_ftp_instance, mock_settings, mock_get, mock_response   

def test_download_client_pass_on_init():
    download_client = DownloadClient()
    
    assert isinstance(download_client, DownloadClient)
    assert not vars(download_client)

def test_download_client_pass_on_ftp_download(tmp_path, mock_dependencies):
    mock_ftp_client, mock_settings, mock_get, mock_response = mock_dependencies

    download_client = DownloadClient()
    download_client.download_list_ftp(tmp_path / "test.txt")

    mock_ftp_client.login.assert_called_once()
    mock_ftp_client.cwd.assert_called_with("/test/path")
    mock_ftp_client.retrbinary.assert_called_once()

def test_download_client_fail_on_ftp_download(tmp_path, mock_dependencies):
    mock_ftp_client, mock_settings, mock_get, mock_response = mock_dependencies
    mock_ftp_client.login.side_effect = Exception("Test error")
    download_client = DownloadClient()
    with pytest.raises(DownloadError):
        download_client.download_list_ftp(tmp_path / "test.txt")
    mock_ftp_client.login.assert_called_once()
    mock_ftp_client.cwd.assert_not_called()
    mock_ftp_client.retrbinary.assert_not_called()

def test_download_pdb_success(tmp_path, mock_dependencies):
    mock_ftp_client, mock_settings, mock_get, mock_response = mock_dependencies

    client = DownloadClient()
    
    # Run the function
    result_path = client.download_pdb("1ab2.pdb", tmp_path)
    
    # Assert requests.get was called correctly
    mock_get.assert_called_once()
    
    # Assert the file was created and contains the chunked data
    assert result_path.exists()
    assert result_path.name == "1ab2.pdb"
    assert result_path.parent.name == "source"
    assert result_path.read_text() == "test file content"

def test_download_pdb_status_error(tmp_path, mock_dependencies):
    mock_ftp_client, mock_settings, mock_get, mock_response = mock_dependencies
    
    # Simulate a 404 Not Found error
    mock_response.status_code = 404
    
    client = DownloadClient()
    
    with pytest.raises(DownloadError, match="404"):
        client.download_pdb("1ab2.pdb", tmp_path)
        
    # Ensure it didn't try to read the content if it failed
    mock_response.iter_content.assert_not_called()

def test_download_pdb_file_error(tmp_path, mock_dependencies):
    mock_ftp_client, mock_settings, mock_get, mock_response = mock_dependencies
    
    # Force an exception to occur the moment iter_content is called
    mock_response.iter_content.side_effect = Exception("Simulated disk error")
    
    client = DownloadClient()
    
    with pytest.raises(FileError, match="Download save failed"):
        client.download_pdb("1ab2.pdb", tmp_path)
