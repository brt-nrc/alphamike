from amfunctions import check_make_dir, download_list_ftp, InputError, FileError, download_pdb, initialize_csv
import os
import subprocess
import csv

class Family:
    """Family class.
    Attributes: barcode - string
                domain_list - list(string)
                family_set - set(string)
                num_family - int
    Methods: check_create_domain(folder_path = pdb)
             create_descriptor(out = desc_tmp, folder_path = pdb/)
             run_mustang(folder_path = pdb)"""
    def __init__(self, b: str, d: list, f: set) -> None:                        # Creates Object
        self.barcode = b
        self.domain_list = d.copy()
        self.family_set = f.copy()
        self.num_family = len(self.family_set)

    def __repr__(self):
        return "{0} -> {1}".format(self.barcode, self.domain_list)              # print() method

    def check_create_domain(self, folder_path: 'path' = 'pdb') -> None:
        """Checks if domain exists, if it does not if creates it."""
        pdb_ext = '.pdb'
        list_name = 'cath-domain-boundaries-v4_1_0.txt'
        path = os.path.abspath(folder_path)                                     # folder_path absolute path
        if not os.path.isfile(list_name):                                       # checks if domain boundaries list is in folder
            download_list_ftp()                                                 # if it doesn't, it downloads it
        for name in self.domain_list:                                           # for each domain
            if not len(name) == 7:                                              # name has to be 7 chars, as cath specs
                raise InputError('Create Domain Name input wrong')
            pdb_domain_file = name + pdb_ext                                    # filename of the requested domain
            pdb_domain_path = os.path.join(path, pdb_domain_file)               # path of the requested domain
            if not os.path.isfile(pdb_domain_path):                             # if file exists, skip creation
                print('Making ', name, ' domain', end='', flush=True)
                domain_range = []                                               # domain range list initialization
                domain_boundaries = []                                          # domain boundaries list initialization
                pdb_main_path = os.path.join(path, 'source')                    # creates path of .pdb sources
                pdb_main_file = name[0:4] + pdb_ext                             # creates .pdb source file
                pdb_main = os.path.join(pdb_main_path, pdb_main_file)           # creates .pdb source file path
                if not os.path.isfile(pdb_main):                                # checks if source file exists
                    try:
                        download_pdb(pdb_main_file, folder_path)                # if it doesn't, download it
                    except Exception as err:
                        print(err)
                with open(list_name) as file:                                   # opens domain boundaries list
                    for line_content in file:                                   # for each line
                        line = line_content.split()                             # creates a list from string
                        if line[0] == name[0:5]:                                # checks if the line describes the domain requested
                            found = True
                            index_sum = 3                                       # initializes index_sum at 3. line[index_sum] = n. of fragments in 1st chain
                            if not int(name[-2:]) == 0:                         # if the last 2 chars of domain is different from 00, we need to find the correct chain description
                                for i in range(int(name[-2:])-1):               # loop for "XX"-1
                                    d = int(line[index_sum])                    # int(n. of fragments)
                                    index_sum += d * 6 + 1                      # goes to the n. of fragments for the next chain
                            index_max = index_sum + int(line[index_sum])*6      # maximum index for the chain
                            if name[4].isdigit():                               # if the chain char is a number
                                domain_boundaries = [e for e in line[index_sum:index_max] if not e == '-' or e.isalpha()]   # creates new list with [0]->n. of fragments and then fragment boundaries
                                domain_boundaries = [int(e) for e in domain_boundaries[::2]]    #
                            elif name[4].isalpha():                             # if chain char is a letter
                                domain_boundaries = [int(e) for e in line[index_sum:index_max] if not (e == '-' or e.isalpha())] # creates new list with [0]->n. of fragments and then fragment boundaries
                            if found:
                                break
                    for i in range(domain_boundaries[0]):               # loop for the n. of fragments
                        domain_range.extend(range(domain_boundaries[1 + i * 2], domain_boundaries[2 + i * 2]+1))    # creates new list with all the pdb numbers included in the chain
                    with open(pdb_main) as pdbfile:                             # open the source file
                        try:
                            with open(pdb_domain_path, "w") as domainfile:      # open the domain file
                                for pdbline in pdbfile:                         # for each line in the source file
                                    pdblinelist = pdbline.split()
                                    if pdblinelist[0] == 'ATOM':                # if the line starts with ATOM
                                        pdbnumber = pdblinelist[5]              # pdb number
                                        chainletter = pdblinelist[4]            # chain letter
                                        if pdbnumber[-1].isalpha():             # if there's a letter at the end of the pdb number
                                            pdbnumber = pdbnumber[:-1]          # take it out
                                        if len(pdblinelist[4]) == 5:            # if the pdb number is the format X0000
                                            pdbnumber = pdblinelist[4][1:]      # separate pdb number and chain letter
                                            chainletter = pdblinelist[4][0]
                                        if (chainletter == name[4]) and (int(pdbnumber) in domain_range): # if the chain char is equal and the pdb number is in range
                                            print(pdbline, file=domainfile, end='') # if they are, copy the row to the domain file
                        except Exception as err:
                            raise FileError("domain file error", err)

    def create_descriptor(self, out: str = 'desc_tmp', pdb_path: 'path' = 'pdb/', folder_path: 'path' = ''):
        """Creates descriptor file as MUSTANG's spec"""
        pdbfiles = [e + '.pdb' for e in self.domain_list]   # Creates new list with filenames + extension of domains
        check_make_dir(folder_path)
        path = os.path.abspath(folder_path)
        out_path = os.path.join(path, out)
        with open(out_path, 'w') as desc:                   # Opens descriptor file
            print('>', pdb_path, file=desc, sep='')         # prints the path to domains
            for e in pdbfiles:
                print('+', e, sep='', file=desc)            # prints the domain list

    def run_mustang(self, filename: str = 'results', mustang_path: 'path' = '') -> None:
        """Runs MUSTANG and saves the identities result"""
        results_filename = filename + '.csv'                    # results filename
        check_make_dir('results')                               # checks if the folder path exists
        out = os.path.join('results', self.barcode+'.html')     # if the result for the structure exists, skip MUSTANG execution
        if not os.path.isfile(out):
            path = os.path.join('results', self.barcode)        # creates output path
            self.create_descriptor()                            # creates descriptor file
            command = [mustang_path + 'mustang-3.2.3', '-o', path, '-f', 'desc_tmp', '-s', 'OFF']   # MUSTANG command
            try:
                subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)   # runs the command and checks if the program completes succesfully

            except Exception as err:
                self.create_descriptor(out=self.barcode, folder_path='missing')
                raise Exception(err)
        try:
            with open(out) as mus_result:                       # opens the result file
                for mus_result_line in mus_result:
                    mus = mus_result_line.split()
                    iden = 'Identity:'
                    if len(mus) > 1:                            # if the line contains something more than decoration
                        if iden in mus[1]:                      # checks if the line contains the identity result
                            if not os.path.exists(results_filename): # if the result csv exists
                                initialize_csv(filename)        # if it doesnt, initialize it
                            with open(results_filename, 'a') as results:
                                writer = csv.writer(results)
                                string_mus = mus_result_line.replace('#', '').replace('<B>', ' ').replace('</B>', ' ') # remove unwanted chars from the string
                                list_mus = string_mus.split()
                                row = [self.barcode, list_mus[1], list_mus[3], list_mus[5], self.num_family, '']
                                writer.writerow(row)     # save identity data to csv
        except Exception as err:
            raise Exception(err)


def find_structures(file: 'path' = 'chwgo.txt') -> list:
    """Finds structures with more than 1 domain linked"""
    structure_list = []                     # initializes structure list
    with open(file) as structures:          # opens input file
        for lines in structures:
            line_content = lines.split()
            num = int(line_content[0])      # number of domains is the fist character in the row
            if num > 1:                     # if the number is more than 1, save the structure
                barcode = line_content[1]   # save barcode
                domain_list = []            # initializes domain list
                family_set = set()         # initializes family set
                for i in range(num):        # for number of domains linked
                    index = 2+3*i           # index for accessing domain and family data
                    domain = line_content[index]    # save domains
                    domain_list.append(domain.replace(',', '')) # append domain do domain list, removes ,
                    family_set.add(line_content[index+1]) # save domain
                structure_list.append(Family(barcode, domain_list, family_set))  # append to output the new structure
    return structure_list
