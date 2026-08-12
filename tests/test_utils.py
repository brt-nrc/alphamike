from pathlib import Path
from alphamike.utils import initialize_csv

def test_initialize_csv_pass(tmp_path):
    test_file = tmp_path / "test.csv"
    initialize_csv(test_file)
    assert test_file.is_file()
    assert test_file.read_text() == "Barcode,Identities,Length,Percentage\n"