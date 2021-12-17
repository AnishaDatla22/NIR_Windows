

# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 13:02:52 2020
@author: Anisha
"""


from Setup import *
from Format_data import *
#**********************************************************************************************
#-------------------------------Data Formatting Functions--------------------------------------
#**********************************************************************************************

def pt_post_scatter_data_format(file_path,file_name,model_name,model,df_final):

    if not os.path.exists(file_path):                      # check path
        os.makedirs(file_path)
    dump(model, open(model_name, 'wb'))                    # save model info

    
    df_write = df_final.round(4).reset_index()
    df_write.to_csv(file_name)                              # write to csv


    final_out_table = FD_Transpose_data(df_final)           # Transpose df_final


    final_out_graph=df_write.to_json(orient='records')      # Convert to json
    final_out_table=final_out_table.to_json(orient='records')

    return final_out_graph,final_out_table


#**********************************************************************************************
#-------------------------------PreTreatment Functions-----------------------------------------
#**********************************************************************************************
def PT_scatter_correction(parent,child, sample,model,model_name, input_file):


    formatted_data = FD_format_data(input_file)

    df_sc=model.fit_transform(formatted_data)


    Model_path = "Models/"+parent+"/"+child+"/scatter_correction/"
    file_name =  Model_path + sample+ "_" +model_name+ ".csv"
    model_name = Model_path + sample+"_"+model_name+'.pkl'

    final_out_graph,final_out_table = pt_post_scatter_data_format(Model_path,file_name,model_name,model,df_sc)

    return final_out_graph, final_out_table # return json structure

def PT_savitzky_golay(parent,child,sample,derivative,polynomial,window,input_file):


    formatted_data = FD_format_data(input_file)
    spectra_values = formatted_data.values                                                       # convert to numpy to feed sav_gol filter
    smoothed = signal.savgol_filter(spectra_values, window, polynomial,derivative,axis=0)
    df_final = pd.DataFrame(smoothed,index=formatted_data.index,columns=formatted_data.columns)   # convert numpy to dataframe

    Model_path = "Models/"+parent+"/"+child+"/pretreatment/"
    file_name = Model_path + sample + "_SG.csv"
    model_name = Model_path + sample+'_SG.pkl'
    sav_gol_param = [window,polynomial,derivative]

    final_out_graph,final_out_table = pt_post_scatter_data_format(Model_path,file_name,model_name,sav_gol_param,df_final)


    return {'smoothedData':final_out_graph,'table':final_out_table}
