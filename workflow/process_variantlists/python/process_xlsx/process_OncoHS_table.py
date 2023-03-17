# -*- coding: utf-8 -*-
"""
Script to sort CLC workbech output OncoHS, to extract the panel specific exons 
with coverage below 100 and to add current inernal variantlist (variantDBi)

Input: xlsx-file from CLC workbench OncoHS workflow, exontableOncoHS.xlxs and
variantDBi.xlsx
Current variantDBi is hardcoded, newer versions of the variantDBi has to be 
updated in this script (line: 142)
Output: xlsx file (sorted OncoHS variantlist with added variantDBi and exon 
information with coverage below 100)

@author: Patrick Basitta
"""

# Import packages
import pandas as pd
import warnings
from xlsxwriter.utility import xl_rowcol_to_cell
import functions_pv.functions_processing_variantlists_xlsx as pv
import argparse
from datetime import datetime

#---------------------------------------
# Using argparse for positinal arguments
#---------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("filename")
args = parser.parse_args()

filename = args.filename

#--------------------------------------------------
# Getting current date and time for log information
#--------------------------------------------------
date_time_now = datetime.now()
# dd/mm/YY H:M:S
dt_string = date_time_now.strftime("%d/%m/%Y %H:%M:%S")
print("Start:", dt_string)
# Processed file
print("Input file:", filename)
print("Output file: output_"+filename)
# Script used
print("Script: processing_OncoHS.py")

#-------------------------------------------------------------------------
# Fixing the warning message "Workbook contains no default style, 
# apply openpyxl's default". The warning.filterswanings() is used to
# exclude the message from the console. The warning points out that while 
# reading the input excel file, the format style of openpyxl's defalut 
# will be used!
#-------------------------------------------------------------------------
warnings.filterwarnings(action = "ignore",\
        message="Workbook contains no default style, apply openpyxl's default")
    
#----------------------------------------
# Getting number of excel sheets (pandas)
#----------------------------------------
es = pd.ExcelFile(filename)
number_all_sheets = len(es.sheet_names)

#----------------------------------------
# Getting names of all sheets (pandas)
#----------------------------------------
names_all_sheets = es.sheet_names

#------------------------------------------------------
# Getting the CLC workbench output data in excel format
#------------------------------------------------------
all_data_sheets = pd.read_excel(filename, sheet_name=None, engine = "openpyxl")
all_data_sheets_lst = list(all_data_sheets.values())

#---------------------------------------------------------------------------   
# Extracting the indices from "coverage", "unfiltered" and "filtered sheets"
#---------------------------------------------------------------------------
index_cov_sheets = pv.extract_index_cov_sheets(number_all_sheets)
index_unfil_sheets = pv.extract_index_unfil_sheets(number_all_sheets)
index_fil_sheets = pv.extract_index_fil_sheets(number_all_sheets)

#----------------------------------------------------------
# Getting exons under min coverage 100 in "coverage sheets" and 
# gene_exon_min_cov_lst
#----------------------------------------------------------

# Getting exon table OncoHS
exon_table_filename = "exontableOncoHS.xlsx"

# Getting gene_exon_min_cov_lst
gene_exon_min_cov_lst = pv.get_gene_exon_minc(index_cov_sheets,\
                                              exon_table_filename,\
                                                  all_data_sheets_lst)

# Log information
print("Process information:")
print("--> Extracting exons with coverage below 100: successful!")    

#----------------------------------------------------------------
# Sorting unfil_sheet using "Reference allel, QUAL and Frequency"
#----------------------------------------------------------------
all_data_sheets_lst = pv.sort_unfil_sheets(index_unfil_sheets, 
                                         all_data_sheets_lst)

#------------------------------------
# Sorting fil_sheet using "Frequency"
#------------------------------------
all_data_sheets_lst = pv.sort_fil_sheets(index_fil_sheets, 
                                         all_data_sheets_lst)


# Log information
print("--> Sorting unfiltered and filtered sheets: sucessful!")

#------------------------------------------------------------------------------
# Rename sheet names and create workbook with repective sheet names
#------------------------------------------------------------------------------
# Rename sheets 
renamed_all_sheets = pv.rename_all_sheets(names_all_sheets,\
                                          index_cov_sheets,\
                                          index_unfil_sheets,\
                                          index_fil_sheets)

# Making cov sheet names list
cov_sheet_names = []
for i in range(len(index_cov_sheets)):
    cov_sheet_name = renamed_all_sheets[index_cov_sheets[i]]
    cov_sheet_names.append(cov_sheet_name)
    
# Making unlist sheet names list
unfil_sheet_names = []
for i in range(len(index_unfil_sheets)):
    unfil_sheet_name = renamed_all_sheets[index_unfil_sheets[i]]
    unfil_sheet_names.append(unfil_sheet_name)

# Making unlist sheet names list
fil_sheet_names = []
for i in range(len(index_fil_sheets)):
   fil_sheet_name = renamed_all_sheets[index_fil_sheets[i]]
   fil_sheet_names.append(fil_sheet_name)
    
# Merge/join internal variantDB (variantDBi) to unfiltered/filtered sheets
# Change to current "Variantenliste" if needed
variantDBi = pd.read_excel("Variantenliste 22_12_15.xlsx")

all_data_sheets_lst = pv.merge_variantDBi_unfil(index_unfil_sheets,\
                                          all_data_sheets_lst,\
                                          variantDBi)

all_data_sheets_lst = pv.merge_variantDBi_fil(index_fil_sheets,\
                                          all_data_sheets_lst,\
                                          variantDBi)

# Log information
print("--> Adding internal variantDB: successful!")

#------------------------------------------------------------------------------
# Workbook--------------------------------------------------------------
#------------------------------------------------------------------------------

writer = pd.ExcelWriter("output_pv/output_"+filename,\
                        engine = "xlsxwriter",
                        engine_kwargs={"options":\
                                       {"strings_to_formulas":\
                                        False,
                                        "strings_to_numers":\
                                        False,
                                        "nan_inf_to_errors":\
                                        False}})
# General paramters  
workbook = writer.book
header_format = workbook.add_format({"bg_color": "#c0c0c0"})
header_text_wrap = workbook.add_format()
header_text_wrap.set_text_wrap()
bottom_format = workbook.add_format({"bottom": 1, "bottom_color": "#000000"})
#bottom_format.set_bottom()
red_format = workbook.add_format({"bg_color": "#FFC7CE"})  
index_below_100_exon = 0


if len(index_cov_sheets) == len(index_unfil_sheets) == len(index_fil_sheets):
        
    for number in range(number_all_sheets):

        all_data_sheets_lst[number].\
            to_excel(writer,\
                     sheet_name =renamed_all_sheets[number],\
                     index = False, header = True)
        
        if renamed_all_sheets[number] in cov_sheet_names:
            
            # Conditional formatting HEADER and "Min coverage!
         
            (max_row, max_col) = all_data_sheets_lst[number].shape
            
            # Getting first cell last cell first row of header
            first_cell_header = xl_rowcol_to_cell(0,max_col-max_col)
            last_cell_header = xl_rowcol_to_cell(0,max_col-1)
            
            # Workaround to style header, getting columns names in list
            cov_header_names_lst = []
            for cov_header_names in all_data_sheets_lst[number].columns:
                cov_header_names_lst.append(cov_header_names)
               
            # Getting index of column "Min coverage"
            col_name_min_cov = "Min coverage"
            index_colname_min_cov =  all_data_sheets_lst[number].\
                columns.get_loc(col_name_min_cov)

            # Getting first cell last cell of the column "Min coverage"
            first_cell = xl_rowcol_to_cell(1,index_colname_min_cov)
            last_cell = xl_rowcol_to_cell(max_row,index_colname_min_cov)
            
            worksheet = writer.sheets[renamed_all_sheets[number]]
            
            # Workaround to style header, rewrite header with stlye
            for count_index, col_names in enumerate(cov_header_names_lst):
                
                worksheet.write(0,count_index, col_names, header_text_wrap)
                
            worksheet.conditional_format(first_cell_header+":"+\
                                         last_cell_header,
                                         {"type":     "unique",
                                         "format": header_format})
            
            worksheet.conditional_format(first_cell+":"+last_cell,
                                        {"type":     "cell",
                                         "criteria": "less than",
                                         "value":     100,
                                         "format":    red_format})
           
            gene_exon_min_cov_str = " ".join(gene_exon_min_cov_lst\
                                            [index_below_100_exon])
                            
            worksheet.write("S13", gene_exon_min_cov_str)
              
            index_below_100_exon = index_below_100_exon + 1
            
        if renamed_all_sheets[number] in unfil_sheet_names:
            
            # Conditional formatting HEADER and "Frequency below 5% AF"
         
            (max_row, max_col) = all_data_sheets_lst[number].shape
            
            # Getting first cell last cell first row of header
            first_cell_header = xl_rowcol_to_cell(0,max_col-max_col)
            last_cell_header = xl_rowcol_to_cell(0,max_col-1)
            
            # Workaround to style header, getting columns names in list
            cov_header_names_lst = []
            for cov_header_names in all_data_sheets_lst[number].columns:
                cov_header_names_lst.append(cov_header_names)
                
            worksheet = writer.sheets[renamed_all_sheets[number]]
             
            # Workaround to style header, rewrite header with stlye
            for count_index, col_names in enumerate(cov_header_names_lst):
                 
                worksheet.write(0,count_index, col_names, header_text_wrap)
                 
            worksheet.conditional_format(first_cell_header+":"+\
                                         last_cell_header,
                                         {"type":     "unique",
                                         "format": header_format})
            
           # Getting index of the row with frequency below 5 %
            index_below_5_lst = []
            for below_5_index, below_5 in enumerate(all_data_sheets_lst[number]\
                                                         ["Frequency"] < 5):
                if below_5 == True:
                    index_below_5_lst.append(below_5_index)
                    #below_5_check = True
                #else:
                   # below_5_check = False
                    
           # if below_5_check == True:
            index_below_5 = index_below_5_lst[0]
            
           #Getting first cell last cell last row above 5% Af
            first_cell_above_5 = xl_rowcol_to_cell(index_below_5\
                                                  ,max_col-max_col)
            last_cell_above_5 = xl_rowcol_to_cell(index_below_5, max_col-1)
            
            worksheet.conditional_format(first_cell_above_5+":"+\
                                          last_cell_above_5,
                                          {"type":     "no_blanks",
                                           "format": bottom_format})
                
            worksheet.conditional_format(first_cell_above_5+":"+\
                                          last_cell_above_5,
                                          {"type":     "blanks",
                                           "format": bottom_format})
        
        if renamed_all_sheets[number] in fil_sheet_names:
            
            # Conditional formatting HEADER and "Freqeuncy below 5% AF
            
            (max_row, max_col) = all_data_sheets_lst[number].shape
            
            # Getting first cell last cell first row of header
            first_cell_header = xl_rowcol_to_cell(0,max_col-max_col)
            last_cell_header = xl_rowcol_to_cell(0,max_col-1)
            
            # Workaround to style header, getting columns names in list
            cov_header_names_lst = []
            for cov_header_names in all_data_sheets_lst[number].columns:
                cov_header_names_lst.append(cov_header_names)
                
            worksheet = writer.sheets[renamed_all_sheets[number]]
             
            # Workaround to style header, rewrite header with stlye
            for count_index, col_names in enumerate(cov_header_names_lst):
                 
                worksheet.write(0,count_index, col_names, header_text_wrap)
                 
            worksheet.conditional_format(first_cell_header+":"+\
                                         last_cell_header,
                                         {"type":     "unique",
                                         "format": header_format})
            
            # Getting index of the row with frequency below 5 %
            index_below_5_lst = []
            for below_5_index, below_5 in enumerate(all_data_sheets_lst[number]\
                                                          ["Frequency"] > 5):
                
                #print(below_5_index, below_5)
                if below_5 == True:
                    index_below_5_lst.append(below_5_index+1) 
                    #below_5_check = True
               # else:
                   # below_5_check = False
                     
           # if below_5_check == True:
            index_below_5 = index_below_5_lst[-1]
            
            #Getting first cell last cell last row above 5% Af
            first_cell_above_5 = xl_rowcol_to_cell(index_below_5\
                                                   ,max_col-max_col)
            last_cell_above_5 = xl_rowcol_to_cell(index_below_5, max_col-1)
            
            worksheet.conditional_format(first_cell_above_5+":"+\
                                        last_cell_above_5,
                                        {"type":     "no_blanks",
                                         "format": bottom_format})
                
            worksheet.conditional_format(first_cell_above_5+":"+\
                                         last_cell_above_5,
                                         {"type":     "blanks",
                                          "format": bottom_format})
            

writer.close()

# Log information
print("--> Writing data to xlsx output file: successful!")
# Getting current date and time for log information
date_time_now = datetime.now()
# dd/mm/YY H:M:S
dt_string = date_time_now.strftime("%d/%m/%Y %H:%M:%S")
print("End:", dt_string)
