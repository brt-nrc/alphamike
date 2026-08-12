import csv
import logging
import tempfile
from pathlib import Path
from subprocess import run
from alphamike.structure import Structure
from alphamike.utils import initialize_csv
from alphamike.settings import settings

logger: logging.Logger = logging.getLogger(__name__)

def run_mustang(structure: Structure, result_folder: Path = Path('results'), aggregate_result_file: Path = Path('aggregate_results.csv')) -> None:
    result_folder.mkdir(exist_ok=True)
    out: Path = result_folder / (structure.barcode+'.html')
    if not out.is_file():
        mustang_output_path: Path = result_folder / structure.barcode
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as desc_tmp:
            desc_tmp_path: Path = Path(desc_tmp.name)
            structure.create_descriptor(out=desc_tmp_path)
            command: list[str] = [str(settings.mustang_path / 'bin' / 'mustang-3.2.3'), '-o', str(mustang_output_path), '-f', str(desc_tmp_path), '-s', 'OFF']
            logger.debug(command)
        try:
            run(command, check=True)
        finally:
            if desc_tmp_path.is_file():
                desc_tmp_path.unlink()
        try:
            with open(out) as mus_result:
                for mus_result_line in mus_result:
                    mus: list[str] = mus_result_line.split()
                    if len(mus) > 1:
                        if 'Identity:' in mus[1]:
                            if not aggregate_result_file.is_file():
                                initialize_csv(aggregate_result_file)
                            with open(aggregate_result_file, 'a', newline='') as results:
                                string_mus: str = mus_result_line.replace('#', '').replace('<B>', ' ').replace('</B>', ' ')
                                list_mus: list[str] = string_mus.split()
                                csv.writer(results).writerow([structure.barcode, list_mus[1], list_mus[3], list_mus[5]])
        except Exception as err:
            raise RuntimeError("Failed to parse Mustang output") from err