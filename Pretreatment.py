

# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 13:02:52 2020
@author: rajesh
"""


from Setup import *

def pt_pre_scatter_data_format(input_file):

    input_data = pd.DataFrame(input_file)                                         # Read input data input will be json

    input_data.set_index('Wavelength (nm)', inplace=True)                         # Set wavelength column as index
    input_data = input_data.round(4)                                              # 4 decimal places only

    return input_data

def pt_post_scatter_data_format(file_path,file_name,df_final):

    if not os.path.exists(file_path):                      # check path
        os.makedirs(file_path)

    df_final = df_final.round(4)
    df_final = df_final.reset_index()
    df_final.to_csv(file_name)                              # write to csv

    print("Graph")
    print(df_final)

    final_out_table = df_final.T                                                                          # Transpose for plotting
    final_out_table = final_out_table.rename(columns=final_out_table.iloc[0]).drop(final_out_table.index[0])                             # Make Sample names as column names
    final_out_table.reset_index(inplace = True)                                                      # Reset index
    final_out_table.rename(columns = {'index' : 'Wavelength (nm)'}, inplace = True)                  # rename index column to

    print("format")
    print(final_out_table)

    final_out_graph=df_final.to_json(orient='records')                           # Convert to json
    final_out_table=final_out_table.to_json(orient='records')

    return final_out_graph,final_out_table

def PT_scatter_correction(parent,child, sample_name,model,model_name, input_file):


    formatted_data = pt_pre_scatter_data_format(input_file)

    df_sc=model.fit_transform(formatted_data)

    file_path = "scatter_correction/"+model_name+"/"+parent+"/"+child+"/"
    file_name = file_path + sample_name + "_" +model_name+ ".csv"

    final_out_graph,final_out_table = pt_post_scatter_data_format(file_path,file_name,df_sc)

    return final_out_graph, final_out_table # return json structure
"""
def PT_savitzky_golay(parentName,childName,sample,derivative,polynomial,window,input_file):


    formatted_data = pt_pre_scatter_data_format(input_file)


    columns=formatted_data.columns
    df_final=pd.DataFrame()
    df_final[formatted_data.columns[0]]=np.around(formatted_data[formatted_data.columns[0]])




    smoothed = signal.savgol_filter(formatted_data, window, polynomial,derivative)
    df_final = pd.DataFrame(smoothed)
    print(df_final)
    file_path = "pretreatment/SavitzkyGolay/"+parentName+"/"+childName+"/"
    file_name = file_path + sample + "_SG.csv"

    final_out_graph,final_out_table = pt_post_scatter_data_format(file_path,file_name,df_final)

    return {'smoothedData':final_out_graph,'table':final_out_table}

"""
def PT_savitzky_golay(parentName,childName,sample,derivative,polynomial,window,input_file):


    formatted_data = pt_pre_scatter_data_format(input_file)


    columns=formatted_data.columns
    df_final=pd.DataFrame()
    df_final[formatted_data.columns[0]]=np.around(formatted_data[formatted_data.columns[0]])


    for col in columns:

    # Get rid of nans
    # NOTE: If you have nans in between your data points, this does the wrong thing,
    # but for the data you show for contiguous data this is fine.
        smoothed=[]
        nonans = formatted_data[col]
        smoothed = signal.savgol_filter(nonans, window, polynomial, deriv=derivative)
        df_final[col]=smoothed

    file_path = "pretreatment/SavitzkyGolay/"+parentName+"/"+childName+"/"
    file_name = file_path + sample + "_SG.csv"

    final_out_graph,final_out_table = pt_post_scatter_data_format(file_path,file_name,df_final)

    return {'smoothedData':final_out_graph,'table':final_out_table}
