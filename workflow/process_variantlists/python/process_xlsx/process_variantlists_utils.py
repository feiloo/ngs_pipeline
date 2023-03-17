# -*- coding: utf-8 -*-
"""
Functions for processing CLC workbench outout of targeted gene panels

Scripts using these functions include processing_OncoHS_xlsx.py, 
processing_DNALunge_xlsx.py and processsing_BRCANESS_xlsx.py

"""

import pandas as pd

# Extracting the indeces from all "coverage sheets" from the data
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


# Extracting the indeces from all "unfiltered sheets" from the data
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


# Extracting the indeces from all "filtered sheets" from the data
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


def sort_unfil_sheets(index_unfil_sheets, all_data_sheets_lst):
    for i_unfil in index_unfil_sheets:
        #print(i_unfil)
        unfil_sheets = all_data_sheets_lst[i_unfil]
        sorted_unfil_sheets = unfil_sheets.sort_values(by = ["Reference allele", 
                                                             "QUAL", 
                                                             "Frequency"], 
                                                       ascending = [True, 
                                                                    False,  
                                                                   False])
        all_data_sheets_lst[i_unfil] = sorted_unfil_sheets
    
    return all_data_sheets_lst
  

def sort_fil_sheets(index_fil_sheets, all_data_sheets_lst):
    for i_fil in index_fil_sheets:
        #print(i_unfil)
        fil_sheets = all_data_sheets_lst[i_fil]
        sorted_fil_sheets = fil_sheets.sort_values("Frequency", axis = 0,
                                                       ascending = False)
        all_data_sheets_lst[i_fil] = sorted_fil_sheets
    
    return all_data_sheets_lst


def merge_variantDBi_unfil(index_unfil_sheets, all_data_sheets_lst, variantDBi):
    for i_merge_unfil in index_unfil_sheets:
        unmerged_unfil_sheets = all_data_sheets_lst[i_merge_unfil]
        merged_unfil_sheets = pd.merge(unmerged_unfil_sheets,\
                            variantDBi,\
                            left_on = ["name dbsnp_v138"],\
                            right_on = ["name dbsnp_v151_ensembl_hg38_no_alt_analysis_set"],\
                            how = "left")
        
        all_data_sheets_lst[i_merge_unfil] = merged_unfil_sheets
        
    return all_data_sheets_lst


def merge_variantDBi_fil(index_fil_sheets, all_data_sheets_lst, variantDBi):
    for i_merge in index_fil_sheets:
        unmerged_fil_sheets = all_data_sheets_lst[i_merge]
        merged_fil_sheets = pd.merge(unmerged_fil_sheets,\
                            variantDBi,\
                            left_on = ["name dbsnp_v138"],\
                            right_on = ["name dbsnp_v151_ensembl_hg38_no_alt_analysis_set"],\
                            how = "left")
            
        all_data_sheets_lst[i_merge] = merged_fil_sheets
    
    return all_data_sheets_lst
    

def rename_all_sheets(names_all_sheets, index_cov_sheets, index_unfil_sheets,\
                      index_fil_sheets):
    
    renamed_all_sheets = [renamed.split("_" "")[0]\
                          for renamed in names_all_sheets]

    # Rename cov_sheets    
    cov_sheets_renamed = map(renamed_all_sheets.__getitem__, index_cov_sheets)
    cov_sheets_renamed = list(cov_sheets_renamed)
    cov_sheets_renamed = [cov_sheets_renamed_c + "_c"\
                          for cov_sheets_renamed_c in cov_sheets_renamed]
        
    # Rename unfil_sheets
    unfil_sheets_renamed = map(renamed_all_sheets.__getitem__,\
                               index_unfil_sheets)
    unfil_sheets_renamed= list(unfil_sheets_renamed)
    unfil_sheets_renamed= [unfil_sheets_renamed_c + "_u"\
                          for unfil_sheets_renamed_c in unfil_sheets_renamed]
        
    # Rename fil_sheets
    fil_sheets_renamed = map(renamed_all_sheets.__getitem__, index_fil_sheets)
    fil_sheets_renamed= list(fil_sheets_renamed)
    fil_sheets_renamed= [fil_sheets_renamed_c + "_f"\
                          for fil_sheets_renamed_c in fil_sheets_renamed]
        
    # Concatenate lists           
    all_sheets_renamed = [item for sublist in\
                          zip(cov_sheets_renamed, unfil_sheets_renamed,\
                              fil_sheets_renamed) for item in sublist] 

    return all_sheets_renamed


def get_gene_exon_minc(index_cov_sheets, exon_table_filename, all_data_sheets_lst):
    all_gene_exon_minc_lst = []
    for i_cov in index_cov_sheets:
        exon_table = pd.read_excel(io = exon_table_filename)

        # Lists of dfs
        cov_sheet_exon_table = [all_data_sheets_lst[i_cov], exon_table]

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
            if updated_lst_gene_exon[i][0] == "TERT-Promoter":
                updated_lst_gene_exon[i].pop(1)
                updated_lst_gene_exon[i][0] = updated_lst_gene_exon[i][0]
                updated_lst_gene_exon[i][-1] = "(Minimum coverage: " + str\
                    (updated_lst_gene_exon[i][-1]) + ")"
                    
            elif updated_lst_gene_exon[i][0] in ["chr3:193.2Mb",\
                                                 "chr4:169.7Mb",\
                                                 "chr5:178.7Mb",\
                                                 "chr7:66.2Mb",\
                                                 "chr7:137.0Mb",\
                                                 "TRDMT1",\
                                                 "chr12:6.9Mb",\
                                                 "chr18:9.7Mb",\
                                                 "chr22:33.6Mb",\
                                                 "chrX:11.3Mb",\
                                                 "chrX:96.1Mb",\
                                                 "chrY:6.7Mb",\
                                                 "chrY:21.7Mb"]:
                updated_lst_gene_exon[i].clear()
                
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



    


