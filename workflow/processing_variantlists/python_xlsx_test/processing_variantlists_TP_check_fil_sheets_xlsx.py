# -*- coding: utf-8 -*-
"""
Script to test/check that oncoHS, BRCAness and DNALunge scripts work correctly. It checks
if in fil sheets VAF is sorted, rs numbers match rs numbers of added internal
variantlist and whether rs numbers of CLC output are in accordance with variant 
interpretation of internal variant list.

@author: Patrick Basitta
"""
def check_fil_sheets(filename, variant_lst):
    
    # Import packages
    import pandas as pd
    import functions_pv_check.functions_processing_variantlists_xlsx_check as pv
    #import argparse
    
    #---------------------------------------
    # Using argparse for positinal arguments
    #---------------------------------------
    #parser = argparse.ArgumentParser()
    #parser.add_argument("filename")
    #args = parser.parse_args()
    
    #filename = args.filename  
    #filename = "output_23_01_04_DNALunge.xlsx"
    #variant_lst = "Variantenliste 22_12_15.xlsx"
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
    with open (filename, "rb") as f:
        test_xlsx = pd.read_excel(f,\
                             sheet_name=None, engine = "openpyxl")
    all_sheets_test_xlsx = list(test_xlsx.values())
    
    #---------------------------------------------------------------------------   
    # Extracting the indices from "coverage", "unfiltered" and "filtered sheets"
    #---------------------------------------------------------------------------
    index_cov_sheets = pv.extract_index_cov_sheets(number_all_sheets)
    index_unfil_sheets = pv.extract_index_unfil_sheets(number_all_sheets)
    index_fil_sheets = pv.extract_index_fil_sheets(number_all_sheets)
    
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
       
    var_lst = pd.read_excel(variant_lst)
    counter = 0
    results = []
    tmp_dict = {}
    
    if len(index_cov_sheets) == len(index_unfil_sheets) == len(index_fil_sheets):
            
        for number in range(number_all_sheets):        
            
            if renamed_all_sheets[number] in fil_sheet_names:
                
                sheet_name = fil_sheet_names[counter]
                
                temp_results = pv.check_fil(all_sheets_test_xlsx,var_lst, number)
                
                tmp_dict["keys"] = sheet_name
                tmp_dict["value"] =  list(temp_results)
                
                results.append(tmp_dict.copy())
                counter = counter + 1
    
    return results
      
# Run test
check_fil_sheets("example_file.xlsx", "Variantenliste 22_12_15.xlsx") 
       

