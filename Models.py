# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 13:02:52 2020

@author: rajesh
"""

from Setup import *

def models(parentName:str, childName:str, type:int):
    if not os.path.isdir('Models'):
        os.makedirs('Models')
    parentMLFolders=os.listdir('Models')
    Mlmodels=[]
    childML=[]
    files=[]
    if type == 0:
        directory = 'Models/'+parentName+'/'+childName
        filetype  = 'json'
        index = -4
    else:
        directory = 'Models/'+parentName+'/'+childName +'/graphs'
        filetype = '.pkl'
        index = -5
    try:
        for i in parentMLFolders:
            for j in os.listdir('Models/'+parentName):
                files=[]
                for k in os.listdir(directory):
                     if filetype in k:
                         files.append(k[:index])
                childML.append({
                        'childFolder':j,
                        'Files':files
                        })

            Mlmodels.append({
            'parent':i,
            'child': childML
            })
            childML=[]
    except:
        files = []
    return files
