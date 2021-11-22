# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 13:02:52 2020

@author: rajesh
"""


from Setup import *

def pt_data_formatting(file_path,file_name,df_final):

    if not os.path.exists(file_path):
        os.makedirs(file_path)

    df_final.to_csv(file_name)
    final_out2=df_final.to_json(orient='records')
    final_out_table = df_final.loc[:, ~df_final.columns.str.contains('^Unnamed')]

    final_out_table=final_out_table.T
    final_out_table.index.names = ['Wavelength']
    final_out_table=df_final.T
    final_out_table.columns=final_out_table.iloc[0]
    final_out_table = final_out_table.iloc[1:]
    final_out_table=final_out_table.reset_index()
    final_out_table.rename(columns = {'index' : 'Wavelength'}, inplace = True)

    final_out_table=final_out_table.to_json(orient='records')

    return final_out2,final_out_table

def scatter_correction(parent,child, sample_name,model,model_name, input_file):


    input_data = pd.DataFrame(input_file)                # Read input data input will be json
    input_data.set_index('Wavelength (nm)', inplace=True)

    df_sc=model.fit_transform(input_data)

    df_sc = df_sc.loc[:, ~df_sc.columns.str.contains('^Unnamed')]
    df_sc=df_sc.reset_index()

    file_path = "scatter_correction/"+model_name+"/"+parent+"/"+child+"/"
    file_name = file_path + sample_name + "_" +model_name+ ".csv"

    final_out,final_out_table = pt_data_formatting(file_path,file_name,df_sc)

    return final_out, final_out_table # return json structure


def savitzky_golay_f(parentName,childName,sample,derivative,polynomial,window,input_data):

   df=pd.DataFrame(input_data)
   df_final=pd.DataFrame()
   df_final2=pd.DataFrame()
   df['Wavelength (nm)'] = df['Wavelength (nm)'].astype(float)
   df2=df.set_index('Wavelength (nm)')
   columns=df2.columns
   df_final[df.columns[0]]=np.around(df[df.columns[0]])
   df_final2[df.columns[0]]=np.around(df[df.columns[0]])



   x = df.iloc[:,0].values

   for col in columns:

    # Get rid of nans
    # NOTE: If you have nans in between your data points, this does the wrong thing,
    # but for the data you show for contiguous data this is fine.
    smoothed=[]
    nonans = df[col]
    if derivative==1:
        smoothed = signal.savgol_filter(nonans, window, polynomial, deriv=derivative, delta=x[1] - x[0])
    else:
        smoothed = signal.savgol_filter(nonans, window, polynomial, deriv=derivative)

    df_final[col]=smoothed

    file_path = "pretreatment/SavitzkyGolay/"+parentName+"/"+childName+"/"
    file_name = file_path + sample + "_SG.csv"

    final_out2,final_out_table = pt_data_formatting(file_path,file_name,df_final)

   return {'smoothedData':final_out2,'table':final_out_table}
