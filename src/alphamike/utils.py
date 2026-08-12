import csv
import logging
from pathlib import Path

logger: logging.Logger = logging.getLogger(__name__)


def initialize_csv(csv_file: Path = Path('results.csv')) -> None:
    with open(csv_file, 'w', newline='') as f:
        writer: csv.Writer = csv.writer(f)
        writer.writerow(['Barcode', 'Identities', 'Length', 'Percentage'])
    logger.info(f"Initialized CSV file: {csv_file}")
