import pytest
from pathlib import Path
import builtins
from unittest.mock import patch

from alphamike.domain_creator import create_domain, CreationError, DownloadError

@pytest.fixture
def mock_dependencies(tmp_path):
    with patch("alphamike.domain_creator.DownloadClient") as mock_dc, \
         patch("alphamike.domain_creator.settings") as mock_settings:
        
        boundaries_file = tmp_path / "fake_boundaries.txt"
        boundaries_file.write_text("")
        mock_settings.ftp_server_filename_domain_boundaries = str(boundaries_file)
        
        yield mock_dc, mock_settings, boundaries_file

@pytest.fixture
def mock_ftp_download(tmp_path):
    with patch("alphamike.domain_creator.DownloadClient") as mock_dc, \
         patch("alphamike.domain_creator.settings") as mock_settings:
        
        boundaries_file = tmp_path / "fake_boundaries.txt"
        mock_settings.ftp_server_filename_domain_boundaries = str(boundaries_file)
        
        yield mock_dc, mock_settings, boundaries_file
    
def mock_download_pdb(pdb_main_file, folder_path):
        source_dir = folder_path / "source"
        source_dir.mkdir(exist_ok=True)
        pdb_main = source_dir / pdb_main_file
        pdb_main.write_text(
            "ATOM      1  N   MET A  25      11.660  -9.967   0.718  1.00 45.42           N  \n"
            "ATOM      2  CA  MET A  26      12.636  -8.877   0.505  1.00 44.97           C  \n"
            "ATOM      3  C   MET A  27      12.180  -7.604   1.218  1.00 43.83           C  \n"
            "ATOM      4  O   MET A  27      11.236  -6.932   0.781  1.00 43.19           O  \n"
            "ATOM   2310  O   VAL A 293       2.569 -14.656  50.916  1.00 68.79           O  \n"
            "ATOM   2311  CB  SER A 294       0.170 -13.791  47.457  1.00 66.86           C  \n"
        )

def test_invalid_domain_name_raises(tmp_path, mock_dependencies):
    mock_dc, mock_settings, boundaries_file = mock_dependencies
    
    with pytest.raises(ValueError, match="Create Domain Name input wrong"):
        create_domain("TOOLONG_NAME", folder_path=tmp_path)

def test_returns_existing_domain_file(tmp_path, mock_dependencies):
    mock_dc, mock_settings, boundaries_file = mock_dependencies
    
    domain = "1ab2C01"
    existing = tmp_path / (domain + ".pdb")
    existing.write_text("ATOM ...")
    
    result = create_domain(domain, folder_path=tmp_path)
    
    assert result == existing
    mock_dc.download_pdb.assert_not_called()

def test_download_error_propagates(tmp_path, mock_dependencies):
    mock_dc, mock_settings, boundaries_file = mock_dependencies
    
    domain = "1ab2C01"
    
    # We must provide some minimal content for boundaries if the code expects to read it
    boundaries_file.write_text("1ab2C X X 1 1 - 100 - C\n")
    
    mock_dc.download_pdb.side_effect = Exception("Network error")
    
    with pytest.raises(DownloadError, match="Error occurred while downloading PDB file"):
        create_domain(domain, folder_path=tmp_path)

def test_full_extraction_logic_with_existing_pdb_file(tmp_path, mock_dependencies):
    mock_dc, mock_settings, boundaries_file = mock_dependencies
    
    domain = "1oaiA00" # 7 chars
    # Format: [0]=Domain(first 5), [1]=?, [2]=?, [3]=num_segments, [4]=start_res, [5]=start_ins, [6]=end_res, [7]=end_ins, [8]=chain
    boundaries_file.write_text("1oaiA X X 1 26 - 293 - A\n")
    
    # We need a fake PDB main file
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    pdb_main = source_dir / "1oai.pdb"
    
    pdb_main.write_text(
        "ATOM      1  N   MET A  25      11.660  -9.967   0.718  1.00 45.42           N  \n"
        "ATOM      2  CA  MET A  26      12.636  -8.877   0.505  1.00 44.97           C  \n"
        "ATOM      3  C   MET A  27      12.180  -7.604   1.218  1.00 43.83           C  \n"
        "ATOM      4  O   MET A  27      11.236  -6.932   0.781  1.00 43.19           O  \n"
        "ATOM   2310  O   VAL A 293       2.569 -14.656  50.916  1.00 68.79           O  \n"
        "ATOM   2311  CB  SER A 294       0.170 -13.791  47.457  1.00 66.86           C  \n"
    )
       
    result = create_domain(domain, folder_path=tmp_path)
    
    assert result == tmp_path / (domain + ".pdb")
    
    # Check domain file contents
    output_content = result.read_text().splitlines()
    
    # Should include residues 26 through 293 (inclusive) on chain A
    assert len(output_content) == 4
    
    joined_output = "\n".join(output_content)
    assert "MET A  25" not in joined_output
    assert "SER A 294" not in joined_output
    assert "MET A  26" in output_content[0]
    assert "VAL A 293" in output_content[-1]

def test_full_extraction_logic_with_mocked_download(tmp_path, mock_dependencies):
    mock_dc, mock_settings, boundaries_file = mock_dependencies
    
    domain = "1oaiA00" # 7 chars
    boundaries_file.write_text("1oaiA X X 1 26 - 293 - A\n")
    
    mock_dc.download_pdb.side_effect = mock_download_pdb
       
    result = create_domain(domain, folder_path=tmp_path)
    
    assert result == tmp_path / (domain + ".pdb")
    mock_dc.download_pdb.assert_called_once_with("1oai.pdb", tmp_path)
    
    # Check domain file contents
    output_content = result.read_text().splitlines()
    
    # Should include residues 26 through 293 (inclusive) on chain A
    assert len(output_content) == 4
    
    joined_output = "\n".join(output_content)
    assert "MET A  25" not in joined_output
    assert "SER A 294" not in joined_output
    assert "MET A  26" in output_content[0]
    assert "VAL A 293" in output_content[-1]

def test_ftp_download_triggered_when_boundaries_missing(tmp_path, mock_ftp_download):
    mock_dc, mock_settings, boundaries_file = mock_ftp_download
    
    domain = "1ab2C01"
    
    # The file doesn't exist yet, which triggers the FTP download.
    # We must simulate the download actually creating the file, 
    # otherwise the rest of the function will crash trying to open it.
    def mock_download_list_ftp(target_file):
        target_file.write_text("1ab2C X X 1 1 - 100 - C\n")
        
    mock_dc.download_list_ftp.side_effect = mock_download_list_ftp
    
    # We force a DownloadError on the PDB download just to stop the function
    # early after the boundaries file is processed, avoiding full extraction.
    mock_dc.download_pdb.side_effect = Exception("Stop early")
    
    with pytest.raises(DownloadError):
        create_domain(domain, folder_path=tmp_path)
        
    mock_dc.download_list_ftp.assert_called_once_with(boundaries_file)


def test_domain_creation_from_chain_segment(tmp_path, mock_ftp_download):
    mock_dc, mock_settings, boundaries_file = mock_ftp_download
    
    domain = "1ab2A03"
    
    # The file doesn't exist yet, which triggers the FTP download.
    # We must simulate the download actually creating the file, 
    # otherwise the rest of the function will crash trying to open it.
    def mock_download_list_ftp(target_file):
        target_file.write_text("1ab2A D03 F00  1  A  172 - A  279 -  2  A  280 - A  405 -  A  522 - A  836 -  1  A  2310 - A  2311 -\n")
        
    mock_dc.download_list_ftp.side_effect = mock_download_list_ftp
    
     # We need a fake PDB main file
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    pdb_main = source_dir / "1ab2.pdb"
    
    pdb_main.write_text(
        "ATOM      1  N   MET A  25      11.660  -9.967   0.718  1.00 45.42           N  \n"
        "ATOM      2  CA  MET A  26      12.636  -8.877   0.505  1.00 44.97           C  \n"
        "ATOM      3  C   MET A  27      12.180  -7.604   1.218  1.00 43.83           C  \n"
        "ATOM      4  O   MET A  27      11.236  -6.932   0.781  1.00 43.19           O  \n"
        "ATOM   2310  O   VAL A 2310       2.569 -14.656  50.916  1.00 68.79           O  \n"
        "ATOM   2311  CB  SER A 2311       0.170 -13.791  47.457  1.00 66.86           C  \n"
    )

    result = create_domain(domain, folder_path=tmp_path)
    
    assert result == tmp_path / (domain + ".pdb")
    
    # Check domain file contents
    output_content = result.read_text().splitlines()
    
    # Should include residues 2310 through 2311 (inclusive) on chain A
    assert len(output_content) == 2
    
    joined_output = "\n".join(output_content)
    assert "MET A  25" not in joined_output
    assert "MET A  27" not in joined_output
    assert "VAL A 2310" in output_content[0]
    assert "SER A 2311" in output_content[-1]

def test_domain_creation_numeric_chain(tmp_path, mock_ftp_download):
    mock_dc, mock_settings, boundaries_file = mock_ftp_download
    
    domain = "2qbg602"
    
    # The file doesn't exist yet, which triggers the FTP download.
    # We must simulate the download actually creating the file, 
    # otherwise the rest of the function will crash trying to open it.
    def mock_download_list_ftp(target_file):
        target_file.write_text("2qbg6 D02 F01  2  6    3 - 6   31 -  6  107 - 6  185 -  1  6   32 - 6  106 -  6    1 - 6    2 - (2)\n")
        
    mock_dc.download_list_ftp.side_effect = mock_download_list_ftp
    
     # We need a fake PDB main file
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    pdb_main = source_dir / "2qbg.pdb"
    
    pdb_main.write_text(
        "ATOM      1  N   MET 6  25      11.660  -9.967   0.718  1.00 45.42           N  \n"
        "ATOM      2  CA  MET 6  26      12.636  -8.877   0.505  1.00 44.97           C  \n"
        "ATOM      3  C   MET 6  32      12.180  -7.604   1.218  1.00 43.83           C  \n"
        "ATOM      4  O   MET 6  105      11.236  -6.932   0.781  1.00 43.19           O  \n"
        "ATOM   2310  O   VAL 6 2310       2.569 -14.656  50.916  1.00 68.79           O  \n"
        "ATOM   2311  CB  SER 6 2311       0.170 -13.791  47.457  1.00 66.86           C  \n"
    )

    result = create_domain(domain, folder_path=tmp_path)
    
    assert result == tmp_path / (domain + ".pdb")
    
    # Check domain file contents
    output_content = result.read_text().splitlines()
    
    # Should include residues 2310 through 2311 (inclusive) on chain A
    assert len(output_content) == 2
    
    joined_output = "\n".join(output_content)
    assert "MET 6  25" not in joined_output
    assert "MET 6  26" not in joined_output
    assert "MET 6  32" in output_content[0]
    assert "MET 6  105" in output_content[-1]

def test_create_domain_with_alpha_pdbnumber(tmp_path, mock_ftp_download):
    mock_dc, mock_settings, boundaries_file = mock_ftp_download
    
    domain = "1ab2A01"
    
    # We must provide some minimal content for boundaries if the code expects to read it
    boundaries_file.write_text("1ab2A X X 1 1 - 100 - C\n")
    
     # We need a fake PDB main file
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    pdb_main = source_dir / "1ab2.pdb"
    
    pdb_main.write_text(
        "ATOM      1  N   MET A  25A      11.660  -9.967   0.718  1.00 45.42           N  \n"
        "ATOM      2  CA  MET A  26      12.636  -8.877   0.505  1.00 44.97           C  \n"
        "ATOM      3  C   MET A  32C      12.180  -7.604   1.218  1.00 43.83           C  \n"
        "ATOM      4  O   MET A  105A      11.236  -6.932   0.781  1.00 43.19           O  \n"
        "ATOM   2310  O   VAL A 2310A       2.569 -14.656  50.916  1.00 68.79           O  \n"
        "ATOM   2311  CB  SER A 2311       0.170 -13.791  47.457  1.00 66.86           C  \n"
    )

    result = create_domain(domain, folder_path=tmp_path)
    
    assert result == tmp_path / (domain + ".pdb")
    
    # Check domain file contents
    output_content = result.read_text().splitlines()
    
    # Should include residues 1 through 100 (inclusive) on chain A
    assert len(output_content) == 3
    
    joined_output = "\n".join(output_content)
    assert "VAL A 2310A" not in joined_output
    assert "MET A 105A" not in joined_output
    assert "MET A  25A" in output_content[0]
    assert "MET A  32" in output_content[-1]

def test_create_domain_with_chain_and_chain_number(tmp_path, mock_ftp_download):
    mock_dc, mock_settings, boundaries_file = mock_ftp_download
    
    domain = "1ab2A01"
    
    # We must provide some minimal content for boundaries if the code expects to read it
    boundaries_file.write_text("1ab2A X X 1 1000 - 3000 - C\n")
    
     # We need a fake PDB main file
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    pdb_main = source_dir / "1ab2.pdb"
    
    pdb_main.write_text(
        "ATOM      1  N   MET A  25      11.660  -9.967   0.718  1.00 45.42           N  \n"
        "ATOM      2  CA  MET A  26      12.636  -8.877   0.505  1.00 44.97           C  \n"
        "ATOM      3  C   MET A  32C      12.180  -7.604   1.218  1.00 43.83           C  \n"
        "ATOM      4  O   MET A  105A      11.236  -6.932   0.781  1.00 43.19           O  \n"
        "ATOM   2310  O   VAL A2310       2.569 -14.656  50.916  1.00 68.79           O  \n"
        "ATOM   2311  CB  SER A2311       0.170 -13.791  47.457  1.00 66.86           C  \n"
    )

    result = create_domain(domain, folder_path=tmp_path)
    
    assert result == tmp_path / (domain + ".pdb")
    
    # Check domain file contents
    output_content = result.read_text().splitlines()
    
    # Should include residues 1 through 100 (inclusive) on chain A
    assert len(output_content) == 2
    
    joined_output = "\n".join(output_content)
    assert "MET A  25" not in joined_output
    assert "MET A  26" not in joined_output
    assert "VAL A2310" in output_content[0]
    assert "SER A2311" in output_content[-1]

def test_creation_error(tmp_path, mock_ftp_download):
    mock_dc, mock_settings, boundaries_file = mock_ftp_download
    
    domain = "1cd2A01"
    
    # We must provide some minimal content for boundaries if the code expects to read it
    boundaries_file.write_text("1cd2A X X 1 1000 - 3000 - C\n")
    
     # We need a fake PDB main file
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    pdb_main = source_dir / "1cd2.pdb"
    
    pdb_main.write_text(
        "ATOM      1  N   MET A  25      11.660  -9.967   0.718  1.00 45.42           N  \n"
    )    
    
     # Save a reference to the real open function so we can use it for reading
    original_open = builtins.open
    
    def custom_open(*args, **kwargs):
        # Extract the mode (it's either the 2nd positional arg, a kwarg, or defaults to 'r')
        mode = kwargs.get("mode", args[1] if len(args) > 1 else "r")
        
        # Only throw the error when the code attempts to WRITE the final domain file
        if mode == "w":
            raise IOError("Simulated write error!")
            
        return original_open(*args, **kwargs)
   
    with patch("builtins.open", side_effect=custom_open):
        with pytest.raises(CreationError):
            create_domain(domain, folder_path=tmp_path)
    