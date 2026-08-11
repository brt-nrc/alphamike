import logging
from pathlib import Path
import tempfile
from subprocess import run
from alphamike.structure import Structure
from alphamike.utils import initialize_csv
from alphamike.settings import settings

logger: logging.Logger = logging.getLogger(__name__)

def run_mustang(structure: Structure, result_folder: Path = Path('results'), aggregate_result_file: Path = Path('aggregate_results.csv')) -> None:
    results_filename: Path = aggregate_result_file
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
        except Exception:
            raise
        finally:
            if desc_tmp_path.is_file():
                desc_tmp_path.unlink()
        try:
            with open(out) as mus_result:
                for mus_result_line in mus_result:
                    mus = mus_result_line.split()
                    iden = 'Identity:'
                    if len(mus) > 1:
                        if iden in mus[1]:
                            if not results_filename.is_file():
                                initialize_csv(aggregate_result_file)
                            with open(results_filename, 'a') as results:
                                string_mus = mus_result_line.replace('#', '').replace('<B>', ' ').replace('</B>', ' ')
                                list_mus = string_mus.split()
                                print(structure.barcode, list_mus[1],  list_mus[3], list_mus[5], sep=',', file=results)
        except Exception as err:
            raise Exception(err)