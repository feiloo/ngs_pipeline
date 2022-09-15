# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# Refacotr OncoHS Rscript

import os
import pandas as pd
import OncoHS_python.functions_panel_analysis as pv
import xlsxwriter

#----------------------------------
# Getting current working directory
#----------------------------------
cwd = os.getcwd()
path_to_data = cwd
print(cwd)
print(path_to_data)
#-----------------
# Getting filename
#-----------------
files = os.listdir()
filename = "22_03_02OncoHSTest_22.xlsx"

# Reading excel file
# Getting number of excel sheets (using openpyxl)
#wb = openpyxl.load_workbook(filename)
#print(type(wb))
#print(wb)
#number_all_sheets = len(wb.sheetnames)
#print(number_all_sheets)

#------------------
# Creating Workbook
#------------------
wb = xlsxwriter.Workbook(filename)
print(wb.worksheets)

#----------------------------------------
# Getting number of excel sheets (pandas)
#----------------------------------------
es = pd.ExcelFile(filename)
#print(noes)
number_all_sheets = len(es.sheet_names)
#print(number_all_sheets)

#----------------------------------------
# Getting names of all sheets (pandas)
#----------------------------------------
names_all_sheets = es.sheet_names
print(names_all_sheets)



#------------------------------------------------------
# Getting the CLC workbench output data in excel format
#------------------------------------------------------
all_data_sheets = pd.read_excel(io=filename, sheet_name=None)
print(all_data_sheets)
all_data_sheets_lst = list(all_data_sheets.values())
#print(all_data_sheets_lst[0])

#---------------------------------------------------------------------------   
# Extracting the indeces from "coverage", "unfiltered" and "filtered sheets"
#---------------------------------------------------------------------------
index_cov_sheets = pv.extract_index_cov_sheets(number_all_sheets)
index_unfil_sheets = pv.extract_index_unfil_sheets(number_all_sheets)
index_fil_sheets = pv.extract_index_fil_sheets(number_all_sheets)

#-------------------------------
# Highlighting min_cov below 100
#-------------------------------



#----------------------------------------------------------------
# Sorting unfil_sheet after "Reference allel, QUAL and Frequency"
#----------------------------------------------------------------
all_data_sheets_lst1 = pv.sort_unfil_sheets(index_unfil_sheets, 
                                         all_data_sheets_lst)

#------------------------------------
# Sorting fil_sheet after "Frequency"
#------------------------------------
all_data_sheets_lst1 = pv.sort_fil_sheets(index_fil_sheets, 
                                         all_data_sheets_lst)



#-------------------------------
## ERROR with openpyxl ###
# Generate output file "openpyxl"
#-------------------------------
writer = pd.ExcelWriter("output_" + filename, engine = "openpyxl")
for i in range(number_all_sheets):
    #print(i)
    all_data_sheets_lst[i].to_excel(writer, sheet_name = names_all_sheets[i],
                                    index = False,
                                    header = True)
writer.save()
writer.close()    

#----------------------------------
# Generate output file "xlsxwriter"
#----------------------------------
writer = pd.ExcelWriter("output_" + filename, engine = "xlsxwriter")
for i in range(number_all_sheets):
    #print(i)
    all_data_sheets_lst[i].to_excel(writer, sheet_name = names_all_sheets[i],
                                    index = False,
                                    header = True)   
writer.save()
writer.close() 


#-------------------------------
# Highlighting min_cov below 100
#-------------------------------
writer = pd.ExcelWriter("output_test_" + filename, engine = "xlsxwriter")
all_data_sheets_lst[0].to_excel(writer, sheet_name = names_all_sheets[0],
                                index = False,
                                header = True)
workbook = writer.book
worksheet = writer.sheets[names_all_sheets[0]]

worksheet.conditional_format(all_data_sheets_lst[0].loc[:,"Min coverage"],
                             {"type": "3_color_scale"})

writer.save()
writer.close() 

min_cov = all_data_sheets_lst[0].loc[:,"Min coverage"]
print(min_cov[0])

def highlight_cells_below_100(min_cov):
    color = "red" if min_cov[0] < 100 else ""
    #print("background-color: {}".format (color))
    return "background-color: {}".format (color)

all_data_sheets_lst[0] = all_data_sheets_lst[0].style.applymap(highlight_cells_below_100,
                                                               color_if_true = "red",
                                                               color_if_false = "",
                       subset=["Min coverage"])


