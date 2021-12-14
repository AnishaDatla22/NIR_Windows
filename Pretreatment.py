

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

def pt_post_scatter_data_format(file_path,file_name,model_name,model,df_final):

    if not os.path.exists(file_path):                      # check path
        os.makedirs(file_path)
    dump(model, open(model_name, 'wb'))                    # save model info

    df_final = df_final.round(4)
    df_final = df_final.reset_index()
    df_final.to_csv(file_name)                              # write to csv


    final_out_table = df_final.T                                                                          # Transpose for plotting
    final_out_table = final_out_table.rename(columns=final_out_table.iloc[0]).drop(final_out_table.index[0])                             # Make Sample names as column names
    final_out_table.reset_index(inplace = True)                                                      # Reset index
    final_out_table.rename(columns = {'index' : 'Wavelength (nm)'}, inplace = True)                  # rename index column to


    final_out_graph=df_final.to_json(orient='records')                           # Convert to json
    final_out_table=final_out_table.to_json(orient='records')

    return final_out_graph,final_out_table



def PT_scatter_correction(parent,child, sample,model,model_name, input_file):


    formatted_data = pt_pre_scatter_data_format(input_file)

    df_sc=model.fit_transform(formatted_data)


    Model_path = "Models/"+parent+"/"+child+"/scatter_correction/"
    file_name =  Model_path + sample+ "_" +model_name+ ".csv"
    model_name = Model_path + sample+"_"+model_name+'.pkl'

    final_out_graph,final_out_table = pt_post_scatter_data_format(Model_path,file_name,model_name,model,df_sc)

    return final_out_graph, final_out_table # return json structure

def PT_savitzky_golay(parent,child,sample,derivative,polynomial,window,input_file):


    formatted_data = pt_pre_scatter_data_format(input_file)

    spectra_values = formatted_data.values                                                       # convert to numpy to feed sav_gol filter
    smoothed = signal.savgol_filter(spectra_values, window, polynomial,derivative,axis=0)
    df_final = pd.DataFrame(smoothed,index=formatted_data.index,columns=formatted_data.columns)   # convert numpy to dataframe

    Model_path = "Models/"+parent+"/"+child+"/pretreatment/"
    file_name = Model_path + sample + "_SG.csv"
    model_name = Model_path + sample+'_SG.pkl'
    sav_gol_param = [window,polynomial,derivative]

    final_out_graph,final_out_table = pt_post_scatter_data_format(Model_path,file_name,model_name,sav_gol_param,df_final)


    return {'smoothedData':final_out_graph,'table':final_out_table}
