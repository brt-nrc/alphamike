from amclass import find_structures
from amfunctions import error_log
import os
import time
from pprint import pprint

if os.path.isfile('results.csv'):   #Creates new result file
    os.remove('results.csv')

structures = find_structures()      # finds structures to analyze
i = 0
s = len(structures)
for structure in structures:
    structure.check_create_domain() # checks if all domains are available
    print("Running MUSTANG on structure ", i, " of ", s, end='\r')
    try:
        e = structure.run_mustang(mustang_path='MUSTANG_v3.2.3/bin/')
    except Exception as err:
        error_log(structure.barcode)
        error_log(err)
    i += 1
print("Done, results in results.csv")
