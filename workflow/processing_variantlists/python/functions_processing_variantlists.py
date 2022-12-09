# -*- coding: utf-8 -*-
"""

Functions for processing CLC workbench outout of targeted gene panels

Scripts using these functions include processing_OncoHS.py, 
processing_DNALunge.py and processsing_BRCANESS.py

@author: Patrick Basitta

"""

import pandas as pd

# Extracting the indices from all "coverage sheets" from the data
def extract_index_cov_sheets(number_all_sheets):
    
    if number_all_sheets % 3 == 0:
         
        if number_all_sheets == 3:
            index_cov_sheets = [0]
          
        else:
            cov_number_sheets = number_all_sheets/3
                        
            index_cov_sheets = [0]
            counter_cov = 0
            for i in range(1,int(cov_number_sheets)):
                counter_cov = counter_cov + 3
                index_cov_sheets.append(counter_cov)
                
    return index_cov_sheets


# Extracting the indices from all "unfiltered sheets" from the data
def extract_index_unfil_sheets(number_all_sheets):
    
    if number_all_sheets % 3 == 0:
         
        if number_all_sheets == 3:
            index_unfil_sheets = [1]
          
        else:
            unfil_number_sheets = number_all_sheets/3
                        
            index_unfil_sheets = [1]
            counter_unfil = 1
            for i in range(1,int(unfil_number_sheets)):
                counter_unfil = counter_unfil + 3
                index_unfil_sheets.append(counter_unfil)
                
    return index_unfil_sheets


# Extracting the indices from all "filtered sheets" from the data
def extract_index_fil_sheets(number_all_sheets):
    
    if number_all_sheets % 3 == 0:
         
        if number_all_sheets == 3:
            index_fil_sheets = [2]
          
        else:
            fil_number_sheets = number_all_sheets/3
                        
            index_fil_sheets = [2]
            counter_fil = 2
            for i in range(1,int(fil_number_sheets)):
                counter_fil = counter_fil + 3
                index_fil_sheets.append(counter_fil)
                
    return index_fil_sheets

# Sorting "unfiltered sheets"
def sort_unfil_sheets(index_unfil_sheets, csv_data_lst):
    for i_unfil in index_unfil_sheets:
        #print(i_unfil)
        unfil_sheets_frq = csv_data_lst[i_unfil]
        # Convert string number in float
        unfil_sheets_temp1_frq = unfil_sheets_frq ["Frequency"].apply\
            (lambda x: x.strip("'"))
        unfil_sheets_temp2_frq = unfil_sheets_temp1_frq.apply\
            (lambda x: x.replace(",","."))
        unfil_sheets_temp3_frq = unfil_sheets_temp2_frq.to_frame()
        unfil_sheets_temp4_frq = unfil_sheets_temp3_frq.astype("float")
        csv_data_lst[i_unfil]["Frequency"] = unfil_sheets_temp4_frq 
        # Convert string number in float
        unfil_sheets_Q = csv_data_lst[i_unfil]
        unfil_sheets_temp1_Q = unfil_sheets_Q["QUAL"].apply\
            (lambda x: x.strip("'"))
        unfil_sheets_temp2_Q = unfil_sheets_temp1_Q.apply\
            (lambda x: x.replace(",","."))
        unfil_sheets_temp3_Q= unfil_sheets_temp2_Q.to_frame()
        unfil_sheets_temp4_Q= unfil_sheets_temp3_Q.astype("float")
        csv_data_lst[i_unfil]["QUAL"] = unfil_sheets_temp4_Q
        
        sorted_unfil_sheets = csv_data_lst[i_unfil].sort_values\
                              (by = ["Reference allele", 
                                     "QUAL", 
                                     "Frequency"], 
                               ascending = [True, 
                                            False,  
                                            False])
        
        csv_data_lst[i_unfil] = sorted_unfil_sheets
    
    return csv_data_lst
  
# Sorting "filtered sheets"
def sort_fil_sheets(index_fil_sheets, csv_data_lst):
    for i_fil in index_fil_sheets:
        #print(i_fil)
        fil_sheets = csv_data_lst[i_fil]
        fil_sheets_temp1 = fil_sheets["Frequency"].apply\
            (lambda x: x.strip("'"))
        fil_sheets_temp2 = fil_sheets_temp1.apply\
            (lambda x: x.replace(",","."))
        fil_sheets_temp3 = fil_sheets_temp2.to_frame()
        fil_sheets_temp4 = fil_sheets_temp3.astype("float")
        csv_data_lst[i_fil]["Frequency"] = fil_sheets_temp4 
        
        sorted_fil_sheets =  csv_data_lst[i_fil].sort_values("Frequency",
                                                       ascending = False)
        csv_data_lst[i_fil] = sorted_fil_sheets
    
    return csv_data_lst
    
# Getting all exons with coverage below 100
def get_gene_exon_minc(index_cov_sheets, exon_table_OncoHS_filename, csv_data_lst):
    all_gene_exon_minc_lst = []
    for i_cov in index_cov_sheets:
        exon_table_OncoHS = pd.read_excel(io = exon_table_OncoHS_filename)

        # Lists of dfs
        cov_sheet_exon_table = [csv_data_lst[i_cov], exon_table_OncoHS]

        # Join dfs to one df
        cov_sheet_exon_table_joined = pd.concat(cov_sheet_exon_table, axis=1,\
                                        join="inner")

        # Get indices of values with coverage <500
        indices_below_100 =cov_sheet_exon_table_joined.\
                                        index[cov_sheet_exon_table_joined\
                                        ["Min coverage"] < 100].tolist()
                                                                               
        # Get gene_name, econ_number and Min coverage
        df_gene_exon_min_cov = cov_sheet_exon_table_joined.\
                  loc[indices_below_100, ["gene_name","exon", "Min coverage"]]
    
        # Convert data/values to list
        lst_gene_exon_min_cov = df_gene_exon_min_cov.values.tolist()

        # Get gene and exons
        updated_lst_gene_names = []
        updated_lst_gene_exon = []
        for i in lst_gene_exon_min_cov:
           # print(i)
            if i[0] not in updated_lst_gene_names:
                updated_lst_gene_names.append(i[0])

        # Getting names and exon number
        for i in updated_lst_gene_names:
            new_lst = []
            new_lst.append(i)
       # print(new_lst)
            for j in lst_gene_exon_min_cov:
                if(j[0]==i):
                    new_lst.append(j[1])
                #new_lst.append(j[2])
            updated_lst_gene_exon.append(new_lst)

        # Get min coverage
        updated_gene_min_cov = []
        for i in updated_lst_gene_names:
            new_lst2 = []
            new_lst2.append(i)
            #print(new_lst2)
            for j in lst_gene_exon_min_cov:
                if(j[0]==i):
                    #new_lst.append(j[1])
                    new_lst2.append(j[2])
            updated_gene_min_cov.append(new_lst2)

        # remove gene name and find min value
        lst_min_cov = []
        for i in updated_gene_min_cov:
            i.pop(0)
            lst_min_cov.append(i)

        min_coverage_lst = list(map(min,lst_min_cov)) 
       
        # final merge/joined
        if len(updated_lst_gene_exon) == len(min_coverage_lst):
            for i in range(len(updated_lst_gene_exon)):
                updated_lst_gene_exon[i].append(min_coverage_lst[i])      
        
        # Editing gene exon min cov string
        for i in range(len(updated_lst_gene_exon)):
            if updated_lst_gene_exon[i][0] == "TERT-Prom":
                updated_lst_gene_exon[i].pop(1)
                updated_lst_gene_exon[i][0] = updated_lst_gene_exon[i][0]
        #updated_lst_gene_exon[i][-1] = "(Minimum coverage: " + \
          #  str(updated_lst_gene_exon[i][-1]) + ")"
                updated_lst_gene_exon[i][-1] = "(Minimum coverage: " + str\
                    (updated_lst_gene_exon[i][-1]) + ")"
            else:
                updated_lst_gene_exon[i][0] = updated_lst_gene_exon[i][0]\
                    + " Exon"
                updated_lst_gene_exon[i][-1] = "(Minimum coverage: " + str\
                    (updated_lst_gene_exon[i][-1]) + ")"

        gene_exon_minc = [add_exon for sublist in updated_lst_gene_exon for \
                          add_exon in sublist]
    
        gene_exon_minc_str = ",".join(map(str,gene_exon_minc))
        gene_exon_minc_str = gene_exon_minc_str.replace("Exon,", "Exon ")
        gene_exon_minc_str = gene_exon_minc_str.\
            replace(",(Minimum", " (Minimum")
        gene_exon_minc_str = gene_exon_minc_str.replace("),", "), ")
        
        lst_maker = []
        lst_maker.append(gene_exon_minc_str)
        all_gene_exon_minc_lst.append(lst_maker)
        
    return all_gene_exon_minc_lst



    


