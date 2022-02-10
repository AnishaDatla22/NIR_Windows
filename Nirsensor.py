# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 13:02:52 2020

@author: Anisha
"""


from Setup import *
from Sensor.scan import *
from Sensor.usb_comm import *

#**********************************************************************************************
#-------------------------------Helper Functions-----------------------------------------
#**********************************************************************************************
def ns_StartScan(res):
    config_table = {2:0,3:1,4:2,5:3,7:4,8:5,9:6,10:7}
    config_id = config_table[int(res)]
    set_active_config(config_id)                     # Set Active scan config

    start_scan(0) # donot store in sd card

    results = get_results() # get scan results
    ref_scan = get_ref_data() # get reference values
    time.sleep(0.3) # wait 300msec until motor is moved to next position
    return results,ref_scan

#**********************************************************************************************
#-------------------------------Get reference data Functions-----------------------------------------
#**********************************************************************************************
def NS_scanRef(res):

    results , ref_scan = ns_StartScan(res)
    # Convert the results into a dataframe
    values = {"Wavelength (nm)":results["wavelength"],"intensity":results["intensity"],"reference":ref_scan["intensity"]}
    df = pd.DataFrame(values)
    df = df[0:results["length"]]
    df.loc[df.intensity > 0, "reflectance"] = df['intensity']/df['reference'] #reflectance = sample/reference
    df['absorption'] = -(np.log10(df['reflectance']))#absorption = -log(reflectance)

    df.to_csv("referrence/ref_"+str(res)+"_.csv")
    df[df.columns[0]]=np.around(df[df.columns[0]])
    df[df.columns[1]]=np.around(df[df.columns[1]],decimals = 5)
    df=df.dropna()
    df=df[["Wavelength (nm)","absorption","reflectance"]]
    df=df[:444]
    df1=df.T.reset_index()
    df1.columns = np.arange(len(df1.columns))


    final_graph=df.to_json(orient='records')
    final_table=df1.to_json(orient='records')


    return {"graph":final_graph}

def NS_mergeALlRef():
    path = 'referrence/'
    result = glob.glob('referrence/ref*.csv')
    df1=pd.DataFrame()

    df=pd.read_csv(result[0])
    df1['Wavelength (nm)']=df['Wavelength (nm)']

    for i in result:
        colname=i.split("_")
        df=pd.read_csv(i)
        df=df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df1[colname[1]]=df['absorption']
    final_out=df1.to_json(orient='records')
    df1.to_csv(path+'Allref.csv')
    return {'table':final_out}

#**********************************************************************************************
#-------------------------------Scan Samples Functions-----------------------------------------
# #Scan_type - 0:Scan 1:ScanOverlay 2:ScanOverlayMulti
#**********************************************************************************************
def NS_scansample(fileName,name,parent,child,res,scan_type):


    date=datetime.datetime.now().date()
    date=str(date)

    path_sample='sample/'+parent+'/'+child+'/'
    if not os.path.isdir(path_sample+date):
        os.makedirs(path_sample+date)

    results , ref_scan = ns_StartScan(res)

    # Convert the results into a dataframe
    df1=pd.read_csv('referrence/ref_'+str(res)+'_.csv')

    values = {"Wavelength (nm)":results["wavelength"],"intensity":results["intensity"],"reference":ref_scan["intensity"]}
    df = pd.DataFrame(values)
    df = df[0:results["length"]]
    df['reference']=df1['intensity']
    df.loc[df.intensity > 0, "reflectance"] = df['intensity']/df['reference'] #reflectance = sample/reference
    df[name] = -(np.log10(df['reflectance']))#absorption = -log(reflectance)
    df=df[["Wavelength (nm)",name]]


    if scan_type == 1:
        fileName=path_sample+str(date)+"/"+name+'_'+str(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))+'_'+str(res)+".csv"
        df.to_csv(fileName,index=False)
    elif scan_type == 2:
        df_final=pd.read_csv(fileName)
        df_final[name]=df[name]
        df_final.to_csv(fileName,index=False)

    df[df.columns[0]]=np.around(df[df.columns[0]])
    df[df.columns[1]]=np.around(df[df.columns[1]],decimals = 5)
    df=df.dropna()
    df=df[:444]

    if scan_type == 1:
        final_out=df.to_json(orient='records')
    elif scan_type == 2:
        final_out=df_final.to_json(orient='records')
    else:
        df.to_csv(path_sample+str(date)+"/"+name+'_'+str(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))+'_'+str(res)+".csv")
        fileName = path_sample+str(date)+"/"+name+'_'+str(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))+'_'+str(res)+".csv"
        df.to_csv(fileName,index=False)
        final_out=df.to_json(orient='records')

    df1=df.T.reset_index()
    df1.columns = np.arange(len(df1.columns))
    final_out1=df1.to_json(orient='records')

    return {'fileName':fileName,'resolution':res,'table':final_out1,'graph':final_out}

def NS_scanoverlaymultiAutomatic(fileName,name,parent,child,res,stime,number):

    for i in range(1,number+1):
        newname = name + str(i)
        result = NS_scansample(fileName,newname,parent,child,res,2)
    return result
