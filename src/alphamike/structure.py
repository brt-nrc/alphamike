from pathlib import Path
from copy import deepcopy


class Structure:
    def __init__(self, barcode: str, domain_list: list) -> None:
        self.barcode: str = barcode
        self.domain_list: list[str] = deepcopy(domain_list)

    def __repr__(self) -> str:
        return f"{self.barcode} -> {self.domain_list}"

    def create_descriptor(self, out: Path = Path('desc_tmp'), pdb_path: Path = Path('pdb/')) -> None:
        pdbfiles: list[str] = [e + '.pdb' for e in self.domain_list]
        with open(out, 'w') as desc:
            print('>', pdb_path, file=desc, sep='')
            for e in pdbfiles:
                print('+', e, sep='', file=desc)