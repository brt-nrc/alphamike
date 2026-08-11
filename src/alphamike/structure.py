from pathlib import Path
from subprocess import run
from copy import deepcopy


class Structure:
    def __init__(self, b: str, d: list) -> None:
        self.barcode = b
        self.domain_list = deepcopy(d)

    def __repr__(self):
        return f"{self.barcode} -> {self.domain_list}"

    def create_descriptor(self, out: Path = 'desc_tmp', pdb_path: Path = 'pdb/') -> None:
        pdbfiles = [e + '.pdb' for e in self.domain_list]
        with open(out, 'w') as desc:
            print('>', pdb_path, file=desc, sep='')
            for e in pdbfiles:
                print('+', e, sep='', file=desc)