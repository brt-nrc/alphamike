from pathlib import Path
import logging

logger: logging.Logger = logging.getLogger(__name__)

def initialize_csv(csv_file: Path = Path('results.csv')) -> None:
    with open(csv_file, 'w') as csv:
        titles = ['Barcode', 'Identities', 'Length', 'Percentage']
        titles_escaped = [t.strip("'[]") for t in titles]
        print(titles_escaped, sep=',', file=csv)
    logging.info(f"Initialized CSV file: {csv_file}")