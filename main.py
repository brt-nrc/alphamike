from amclass import find_structures
import os
import time
from pprint import pprint

if os.path.isfile('results.csv'):   #Creates new result file
    os.remove('results.csv')

structures = find_structures()      # finds structures to analyze
missing_barcodes = {}
for structure in structures:
    structure.check_create_domain() # checks if all domains are available
    try:
        e = structure.run_mustang(mustang_path='MUSTANG_v3.2.3/bin/')
    except Exception as err:
        print(err)
        missing_barcodes[structure.barcode] = err  # missing barcodes for debug purposes
print("Missing results: ", len(missing_barcodes))
pprint(missing_barcodes)
