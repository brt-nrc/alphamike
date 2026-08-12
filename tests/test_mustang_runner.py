import builtins
from pathlib import Path
import pytest
import subprocess
from unittest.mock import patch, MagicMock
from alphamike.mustang_runner import run_mustang

def mock_subprocess_run(command, check):
    # command[2] is the output prefix (e.g., 'results/test_protein')
    # Mustang appends '.html' to it.
    output_html = Path(command[2] + ".html")
    
    # Write a fake Mustang HTML output line that matches the parsing logic
    fake_content = "# Identity: <B>     317</B>/<B>318</B> (<B> 99.7%</B>)\n"
    output_html.write_text(fake_content)

@patch("alphamike.mustang_runner.run", side_effect=mock_subprocess_run)
def test_mustang_runner_success(mock_run,tmp_path):
    mock_structure = MagicMock()
    mock_structure.barcode = "00000101"
    mock_structure.domain_list = [1,2]
    
    results_folder = tmp_path / "results"
    results_folder.mkdir()

    aggregate_csv = tmp_path/'aggregate.csv'
    if aggregate_csv.is_file():
        aggregate_csv.unlink()
    
    # Call the function
    run_mustang(mock_structure, results_folder, aggregate_csv)
    
    # Check that the dummy HTML file was created
    mock_structure.create_descriptor.assert_called_once()
    mock_run.assert_called_once()

    assert aggregate_csv.is_file()
    assert "00000101,317,318,99.7%\n" in aggregate_csv.read_text() 

@patch("alphamike.mustang_runner.run")
def test_mustang_runner_skip(mock_run, tmp_path):
    mock_structure = MagicMock()
    mock_structure.barcode = "test1"
    mock_structure.domain_list = [1,2]
    
    results_folder = tmp_path / "results"
    results_folder.mkdir()
    results_file = results_folder / (mock_structure.barcode + '.html')
    results_file.touch()

    run_mustang(mock_structure, results_folder)
    
    mock_run.assert_not_called()

@patch("alphamike.mustang_runner.run")
def test_mustang_runner_cleanup_on_failure(mock_run, tmp_path):
    mock_structure = MagicMock()
    mock_structure.barcode = "test_fail"
    
    mock_run.side_effect = subprocess.CalledProcessError(1, "mustang")
    
    results_folder = tmp_path / "results"
    results_folder.mkdir()
    
    with pytest.raises(subprocess.CalledProcessError):
        run_mustang(mock_structure, results_folder)
        
    mock_structure.create_descriptor.assert_called_once()
    
    tmp_file_path = mock_structure.create_descriptor.call_args.kwargs['out']
    
    assert not tmp_file_path.exists()

@patch("alphamike.mustang_runner.run", side_effect=mock_subprocess_run)
def test_mustang_exception_on_parse_fail(mock_run, tmp_path):
    mock_structure = MagicMock()
    mock_structure.barcode = "results_fail"
    mock_structure.domain_list = [1,2]

    results_folder = tmp_path / "results"
    results_folder.mkdir()

    aggregate_csv = tmp_path/'aggregate.csv'
    if aggregate_csv.is_file():
        aggregate_csv.unlink()

    original_open = builtins.open

    def custom_open(*args, **kwargs):
        # Extract the mode (it's either the 2nd positional arg, a kwarg, or defaults to 'r')
        mode = kwargs.get("mode", args[1] if len(args) > 1 else "r")
        
        # Only throw the error when the code attempts to WRITE the final domain file
        if mode == "r":
            raise IOError("Simulated read error!")
            
        return original_open(*args, **kwargs)
   
    with patch("builtins.open", side_effect=custom_open):
        with pytest.raises(RuntimeError):
            run_mustang(mock_structure, results_folder)