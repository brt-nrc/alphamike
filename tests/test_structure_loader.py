from pathlib import Path
from alphamike.structure import Structure
from alphamike.structure_loader import StructureLoader

def test_load_single_structure(tmp_path):
    input_file: Path  = tmp_path / "single_structure.txt"
    input_file.write_text("""2	0000000003020103010200010101010000000000	1q32C02	3.30.870.20	236	,3sq7C02	3.30.870.20	248	****""")
    loader = StructureLoader(input_file)
    structures = loader.load_structures()
    assert len(structures) == 1
    assert structures[0].barcode == "0000000003020103010200010101010000000000"
    assert structures[0].domain_list == ["1q32C02", "3sq7C02"]

def test_load_multiple_structures(tmp_path):
    input_file: Path = tmp_path / "multiple_structures.txt"
    with open(input_file, "w") as test_file:
        print("""2	1111111111111111111111111111111111111111	2ab1A02	1.2.3.4	100, 3ab1A02	1.2.3.4	100 ****""", file=test_file)
        print("""3	2222222222222222222222222222222222222222	3bcdE01	5.6.7.8	200, 4efgF01	5.6.7.8	200, 5hijkL01	5.6.7.8	200""", file=test_file)

    loader = StructureLoader(input_file)
    structures = loader.load_structures()
    assert len(structures) == 2
    assert structures[0].barcode == "1111111111111111111111111111111111111111"
    assert structures[0].domain_list == ["2ab1A02", "3ab1A02"]
    assert structures[1].barcode == "2222222222222222222222222222222222222222"
    assert structures[1].domain_list == ["3bcdE01", "4efgF01", "5hijkL01"]

def test_load_only_structures_with_one_domain(tmp_path):
    input_file: Path = tmp_path / "one_domain_structures.txt"
    with open(input_file, "w") as test_file:
        print("""2	1111111111111111111111111111111111111111	2ab1A02	1.2.3.4	100,   3ab1A02	1.2.3.4	100 ****""", file=test_file)
        print("""1	2222222222222222222222222222222222222222	3bcdE01	5.6.7.8	200,   4efgF01	5.6.7.8	200,  5hijkL01	5.6.7.8	200""", file=test_file)
        print("""3	3333333333333333333333333333333333333333	4ertE01	5.6.7.8	200,   4abcF01	5.6.7.8	200,  5bgtL01	5.6.7.8	200""", file=test_file)

    loader = StructureLoader(input_file)
    structures = loader.load_structures()
    assert len(structures) == 2
    assert structures[0].barcode == "1111111111111111111111111111111111111111"
    assert structures[0].domain_list == ["2ab1A02", "3ab1A02"]
    assert structures[1].barcode == "3333333333333333333333333333333333333333"
    assert structures[1].domain_list == ["4ertE01", "4abcF01", "5bgtL01"]
