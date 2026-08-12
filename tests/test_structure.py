from pathlib import Path
from alphamike.structure import Structure

def test_repr():
    s = Structure("ABC123", ["domain1", "domain2"])
    assert repr(s) == "ABC123 -> ['domain1', 'domain2']"


def test_create_descriptor(tmp_path):
    out_file = tmp_path / "desc.txt"
    s = Structure("ABC123", ["domain1", "domain2"])
    s.create_descriptor(out=out_file, pdb_path=Path("pdb/"))

    content = out_file.read_text()
    assert ">pdb" in content
    assert "+domain1.pdb" in content
    assert "+domain2.pdb" in content
