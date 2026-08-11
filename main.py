import json
import time
import logging
import argparse
from pathlib import Path
from alphamike.structure_loader import StructureLoader
from alphamike.domain_creator import create_domain
from alphamike.mustang_runner import run_mustang

logging.basicConfig(level=logging.DEBUG)
logger: logging.Logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description="Run Mustang on a list of structures")
parser.add_argument("input_file", type=Path, help="Path to the input file")
parser.add_argument("result_folder", type=Path, help="Path to the result folder")
parser.add_argument("aggregate_result_file", type=Path, help="Path to the aggregate result file")



def main(input_file: Path, result_folder: Path, aggregate_result_file: Path) -> None:
    if aggregate_result_file.is_file():
        aggregate_result_file.unlink()
        logger.info(f"Deleted existing aggregate result file: {aggregate_result_file}")

    structure_loader: StructureLoader = StructureLoader(input_file)
    structure_list: list = structure_loader.load_structures()

    tic1 = time.perf_counter()

    for idx,structure in enumerate(structure_list, start=1):
        for domain in structure.domain_list:
            logger.info(f"Creating domain {domain} for structure {structure.barcode} ({idx}/{len(structure_list)})")
            create_domain(domain)

    toc1 = time.perf_counter()
    logger.info(f"Domains created in {toc1 - tic1:0.4f} seconds")

    tic2 = time.perf_counter()
    failed_barcodes: dict[str, str] = {}
    successful_count = 0

    for idx, structure in enumerate(structure_list, start=1):
        logger.debug(f"Processing Mustang for {structure.barcode} ({idx}/{len(structure_list)})...")
        try:
            run_mustang(structure, result_folder=result_folder, aggregate_result_file=aggregate_result_file)
            successful_count += 1
        except Exception as err:
            logger.error(f"Error running Mustang for structure {structure.barcode}: {err}")
            failed_barcodes[structure.barcode] = str(err)

    toc2 = time.perf_counter()
    logger.info(f"Mustang in {toc2-tic2:0.4f} seconds")
    logger.info(f"Successful runs: {successful_count}/{len(structure_list)}")
    if failed_barcodes:
        logger.warning(f"Missing results: {len(failed_barcodes)}: {json.dumps(failed_barcodes, indent=4)}")



if __name__ == "__main__":
    args = parser.parse_args()

    main(args.input_file, args.result_folder, args.aggregate_result_file)