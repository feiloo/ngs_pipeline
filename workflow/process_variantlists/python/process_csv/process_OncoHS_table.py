# -*- coding: utf-8 -*-
"""

Script to sort CLC workbech output OncoHS and extract exons 
with coverage below 100

Input: csv-files
Output: pandas data frames

@author: Patrick Basitta

"""

# Refacotr OncoHS Rscript

import os
import pandas as pd
import OncoHS_python.functions_processing_variantlists as pv

#----------------------------------
# Getting current working directory
#----------------------------------
cwd = os.getcwd()
path_to_data = cwd
print(cwd)
print(path_to_data)
#-----------------
# Getting csv.filename
#-----------------
files_in_dir = os.listdir()
csv_files = list(filter(lambda f: f.endswith(".csv"), files_in_dir))

csv_data_lst = []  

for i in range(len(csv_files)):
    with open(csv_files[i]) as csv_file:
        temp_df = pd.read_csv(csv_file, sep=";")
        csv_data_lst.append(temp_df)
        
#---------------------------------------------------------------------------   
# Extracting the indices from "coverage", "unfiltered" and "filtered sheets"
#---------------------------------------------------------------------------
index_cov_sheets = pv.extract_index_cov_sheets(len(csv_data_lst))
index_unfil_sheets = pv.extract_index_unfil_sheets(len(csv_data_lst))
index_fil_sheets = pv.extract_index_fil_sheets(len(csv_data_lst))

#----------------------------------------------------------
# Getting exons under min coverage 100 in "coverage sheets" and 
# gene_exon_min_cov_lst
#----------------------------------------------------------

# Getting exon table OncoHS
exon_table_OncoHS_filename = "exontableOncoHS.xlsx"

# Getting gene_exon_min_cov_lst
gene_exon_min_cov_lst = pv.get_gene_exon_minc(index_cov_sheets,\
                                              exon_table_OncoHS_filename,\
                                                  csv_data_lst)

#----------------------------------------------------------------
# Sorting unfil_sheet using "Reference allel, QUAL and Frequency"
#----------------------------------------------------------------
csv_data_lst = pv.sort_unfil_sheets(index_unfil_sheets, 
                                         csv_data_lst)

#------------------------------------
# Sorting fil_sheet using "Frequency"
#------------------------------------
csv_data_lst = pv.sort_fil_sheets(index_fil_sheets, 
                                         csv_data_lst)



