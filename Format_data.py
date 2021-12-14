# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 11:22:00 2021

@author: Anisha
"""


from Setup import *


def FD_format_data(input_file):
    input_data = pd.DataFrame(input_file)                                         # Read input data input will be json

    input_data.set_index('Wavelength (nm)', inplace=True)                         # Set wavelength column as index
                                                                                  # TODO: use regex to match column name and rename to Wavelength (nm)
    input_data = input_data.round(4)                                              # 4 decimal places only
    input_data.dropna(axis=0,how='all',inplace=True)                              # Drop any row with all NaN
    input_data.dropna(axis=1,how='all',inplace=True)                              # Drop any column with all NaN
    return input_data

def FD_Transpose_data(input_data):

    input_data = input_data.round(4)
    input_data=input_data.reset_index()
    input_data = input_data.T                                                                   # Transpose for plotting
    input_data =input_data.rename(columns=input_data.iloc[0]).drop(input_data.index[0])         # Make Sample names as column names
    input_data.reset_index(inplace = True)                                                      # Reset index
    input_data.rename(columns = {'index' : 'Wavelength (nm)'}, inplace = True)                  # rename index column to
    return input_data
