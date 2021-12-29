# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 14:29:52 2021

@author:Anisha
"""
from Setup import *

def PM_parameters():
    param = {"Poultry": ["Moisture Content","Fat Content","Protein Content","Fiber Content","Ash Content","Starch Content"],
             "Agri":["Moisture Content", "Fat Content", "Protein Content","Adulteration"],
             "Dairy":["Moisture Content", "Fat Content", "Protein Content","Adulteration"],
             "Pharma":["Granulation End Point","Blend Uniformity","Content Uniformity","Assay Content","Moisture Content"]
     }

    parameters = json.dumps(param,indent=4)
    return parameters


def PM_categories():

    cat = {"Poultry": ["Chick","Broiler","Breeder","Layer","Others"],
            "Agri":["Grains", "Oils", "Fruits","Vegetables","Others"],
            "Dairy":["Milk", "Cheese/Butter", "Whey","Cassein","Others"],
            "Pharma":["Granulation","Blending","Drying","Compression","Process Monitoring","Real-time Process Understanding","Predictive Analytics"]
          }
    categories = json.dumps(cat,indent=4)
    return categories          
