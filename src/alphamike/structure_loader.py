from pathlib import Path
from alphamike.structure import Structure

class StructureLoader:
    def __init__(self, file_path: Path):
        self.file_path = file_path

    def load_structures(self) -> list:
        structure_list: list[Structure] = []
        with open(self.file_path) as structures:
            for lines in structures:
                line_content:list[str] = lines.split()
                num: int = int(line_content[0])
                if num > 1:
                    barcode: str = line_content[1]
                    domain_list: list[str] = []
                    for i in range(num):
                        domain: str = line_content[2 + 3 * i]
                        domain_list.append(domain.replace(',', ''))
                    structure_list.append(Structure(barcode, domain_list))
        return structure_list