from amclass import find_structures
import os
import time
from pprint import pprint

if os.path.isfile('results.csv'):   #Creates new result file
    os.remove('results.csv')

structures = find_structures()      # finds structures to analyze
tic1 = time.perf_counter()          # performance debug
i = 0
for structure in structures:
    structure.check_create_domain() # checks if all domains are available
    i += 1
toc1 = time.perf_counter()
tic2 = time.perf_counter()
missing_barcodes = {}               # missing barcodes for debug purposes
for structure in structures:
    try:
        e = structure.run_mustang()
    except Exception as err:
        print(err)
        missing_barcodes[structure.barcode] = err
toc2 = time.perf_counter()
print(f"Domains in {toc1-tic1:0.4f} seconds")
print(f"Mustang in {toc2-tic2:0.4f} seconds")
print("Missing results: ", len(missing_barcodes))
pprint(missing_barcodes)
