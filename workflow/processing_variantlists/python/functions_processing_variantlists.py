# -*- coding: utf-8 -*-
"""
Created on Thu Sep  1 16:51:36 2022

@author: 50118212
"""

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

#def highlight_min_cov_below_100(index_cov_sheets, all_data_sheets_lst):
    

def sort_fil_sheets(index_fil_sheets, all_data_sheets_lst):
    for i_fil in index_fil_sheets:
        #print(i_unfil)
        fil_sheets = all_data_sheets_lst[i_fil]
        sorted_fil_sheets = fil_sheets.sort_values(by = "Frequency", 
                                                       ascending = False)
        all_data_sheets_lst[i_fil] = sorted_fil_sheets
    
    return all_data_sheets_lst
    



