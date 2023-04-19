# -*- coding: utf-8 -*-
"""
Created on Wed Jan 18 13:02:03 2023

@author: Patrick Basitta

Script in progress!

Short description:

This script generates a dummy DNPM dataset including different IDs, PIDs and
FIDs; data values for all the variants are static (prerequisites: 
"test_dnpm_data.xlsx must be present!).

Furthermore "http://testuserpb:testpw@127.0.0.1:5984/" must be set up prior
script execution. 
        
"""

import pycouchdb
from datetime import datetime
import os
import pandas as pd
import json
import random

# os.listdir()
# Get empty dicts
NGS_Befund_dict = {}
Metadaten_dict = {}
Einfache_Variante_dict = {}
CNVs_dict = {}
DNA_Fusion_dict = {}
RNA_Fusion_dict = {}
RNA_Seq_dict = {}

# Get file
file_dnpm_data="test_dnpm_data.xlsx"

# Get dnpm_data
with open (file_dnpm_data, "rb") as f:
    dnpm_data = pd.read_excel(f,\
                         sheet_name=None, engine = "openpyxl")

# Get sheet names
sheet_names = list(dnpm_data.keys())

# Get Paramter and Auspraegung as dicts
for i in range(len(sheet_names)):
    str = sheet_names[i]+"_dict"
    locals()[str] = dict(zip(dnpm_data[sheet_names[i]]["Parameter"], \
                    dnpm_data[sheet_names[i]]["Auspraegung"]))
  
# Combine dicts
NGS_Befund_dict["Metadaten"] = Metadaten_dict 
NGS_Befund_dict["EinfacheVariante"] = Einfache_Variante_dict
NGS_Befund_dict["CNVs"] = CNVs_dict 
NGS_Befund_dict["DNAFusionen"] = DNA_Fusion_dict
NGS_Befund_dict["RNAFusionen"] = RNA_Fusion_dict
NGS_Befund_dict["RNASeq"] = RNA_Seq_dict 

NGS_Befund_json_object = json.dumps(NGS_Befund_dict, \
                                  indent=len(NGS_Befund_dict)) 

# Connect to server
server = pycouchdb.Server("http://testuserpb:testpw@127.0.0.1:5984/")
server.info()

# Create DB
dnpm_DB = server.create("dnpm_genetischer_kerndatensatz")

# Create data and add to dnpm_DB (getting the data from one pyhton script???)
new_doc = dnpm_DB.save(NGS_Befund_dict)

# Create test data random
for i in range(100):
    NGS_Befund_dict["ID"] = random.randint(3,100000)
    NGS_Befund_dict["PID"] = random.randint(3,100000)
    NGS_Befund_dict["FID"] = random.randint(3,100000)
    dnpm_DB.save(NGS_Befund_dict)


# Design map function in views
_doc = {
        "_id": "_design/pat",
          "views": {
            "ID": {
              "map": "function(doc) {emit(doc.ID, \
                                    {Patient:doc.Patient,\
                                     Probe:doc.Probe,\
                                     Erstellungsdatum:doc.Erstellungsdatum,\
                                     Sequenzierungsart:doc.Sequenzierungsart,\
                                     Metadaten:doc.Metadaten,\
                                     Tumorzellgehalt:doc.Tumorzellgehalt,\
                                     TumorMutationalBurdenTMB:doc.TumorMutationalBurden,\
                                     BRCAness:doc.BRCAness,\
                                     MSI:doc.MSI,\
                                     EinfacheVariante:doc.EinfacheVariante,\
                                     CNVs:doc.CNVs,\
                                     DNAFusionen:doc.DNAFusionen,\
                                     RNAFusionen:doc.RNAFusionen,\
                                     RNASeq:doc.RNASeq}); \
                    }"
                }
            }
        }
          

# Deploy map function                   
doc = dnpm_DB.save(_doc)
list(dnpm_DB.query("pat/ID", key = 2))

# command line
# one find
# curl -X GET 'http://testuserpb:testpw@127.0.0.1:5984/dnpm_genetischer_kerndatensatz/_design/pat/_view/ID?key=2'
# oder 
# curl -X GET http://testuserpb:testpw@127.0.0.1:5984/dnpm_genetischer_kerndatensatz/_design/pat/_view/ID?key=2
# specific finds
# curl -gv http://testuserpb:testpw@127.0.0.1:5984/dnpm_genetischer_kerndatensatz/_design/pat/_view/ID?keys=[2,340]
# find a range
# curl -X GET 'http://testuserpb:testpw@127.0.0.1:5984/dnpm_genetischer_kerndatensatz/_design/pat/_view/ID?startkey=2&endkey=400'
# Windows 
# curl -X GET http://testuserpb:testpw@127.0.0.1:5984/dnpm_genetischer_kerndatensatz/_design/pat/_view/ID --get --data-urlencode startkey=2 --data-urlencode endkey=400
 
