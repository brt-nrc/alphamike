import json
import time
import logging
import argparse
from pathlib import Path
from pprint import pprint
from alphamike.structure_loader import StructureLoader
from alphamike.domain_creator import create_domain
from alphamike.mustang_runner import run_mustang

logging.basicConfig(level=logging.DEBUG)
logger: logging.Logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description="Run Mustang on a list of structures")
parser.add_argument("input_file", type=str, help="Path to the input file")
parser.add_argument("result_folder", type=str, help="Path to the result folder")
parser.add_argument("aggregate_result_file", type=str, help="Path to the aggregate result file")



def main(input_file: Path, result_folder: Path, aggregate_result_file: Path) -> None:
    if aggregate_result_file.is_file():
        aggregate_result_file.unlink()
        logging.info(f"Deleted existing aggregate result file: {aggregate_result_file}")

    structure_loader: StructureLoader = StructureLoader(input_file)
    structure_list: list = structure_loader.load_structures()

    tic1 = time.perf_counter()
    i = 0
    for structure in structure_list:
        for domain in structure.domain_list:
            logging.info(f"Creating domain {domain} for structure {structure.barcode} ({i+1}/{len(structure_list)})")
            create_domain(domain)
        i += 1
    toc1 = time.perf_counter()
    logging.info(f"Domains created in {toc1 - tic1:0.4f} seconds")

    tic2 = time.perf_counter()
    missing_barcodes = {}
    for structure in structure_list:
        try:
            run_mustang(structure, result_folder=result_folder, aggregate_result_file=aggregate_result_file)
        except Exception as err:
            logging.error(f"Error running Mustang for structure {structure.barcode}: {err}")
            missing_barcodes[structure.barcode] = str(err)
    toc2 = time.perf_counter()
    logging.info(f"Mustang in {toc2-tic2:0.4f} seconds")
    logging.warning(f"Missing results: {len(missing_barcodes)}: {json.dumps(missing_barcodes, indent=4)}")



if __name__ == "__main__":
    args = parser.parse_args()
    input_file: Path = Path(args.input_file)
    result_folder: Path = Path(args.result_folder)
    aggregate_result_file: Path = Path(args.aggregate_result_file)

    main(input_file, result_folder, aggregate_result_file)