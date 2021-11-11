# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 13:02:52 2020

@author: rajesh
"""


from Setup import *
from Pretreatment import *
from Nirsensor import *
from NIR_Software.authentication.auth import Auth
from NIR_Software.sensor.scan import Scan
from Analysis import *
from Models import *


app = FastAPI(
title="NIR Spectroscopy"
)


origins = [
    "http://localhost:8000",
    "http://localhost:8000/uploadFile",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sensorOpen = 0

if __name__ == '__main__':
    uvicorn.run("main:app",host="0.0.0.0",workers=1,port=8000)



JSONObject = Dict[AnyStr, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject]



@app.post("/SNV",tags=['Transform Algorithms'])
def tr_algo_sn(parentName:str, childName:str, sample:str, inputf: JSONStructure = None):
        SNV = snv()
        final_out,final_out_table = scatter_correction(parentName, childName, sample,SNV,'T_SNV', inputf)
        return {'snv':final_out,'table':final_out_table}

@app.post("/MSC",tags=['Transform Algorithms'])
def tr_algo_msc(parentName:str, childName:str, sample:str, inputf: JSONStructure = None):
        MSC = msc()
        final_out,final_out_table = scatter_correction(parentName, childName, sample,MSC,'T_MSC', inputf)
        return {'msc':final_out,'table':final_out_table}


@app.post('/plsAlgoritm',tags=['Ml Algorithms'])
def PLS_Algorithm(parentName:str,childName:str,sample: str,scatterCorrection: str,window: int, ploynomial: int,derivative: int, inputf: JSONStructure = None):

   final_data = pls_func(parentName,childName,sample,scatterCorrection,window,ploynomial,derivative,inputf)

   return final_data




@app.get("/pls",tags=['Ml Algorithms'])
def PLS_regression():

    global df
    df_p=df.T.reset_index()
    df_p.rename(columns=df_p.iloc[0])
    df_p.columns=df_p.iloc[0]
    df_p=df_p.drop(df_p.index[0])
    print(df_p)

    x_pls=df_p.drop(['Wavelength (nm)'], axis=1).values
    x_pls=signal.savgol_filter(x_pls, 17, polyorder = 2,deriv=2)

    print(x_pls)

    y_pred=pls.predict(x_pls)
    print(y_pred)
    df_final=pd.DataFrame(y_pred)
    df_final.columns=['% Moisture Content','% Oil Content']
    df_final=df_final.round(decimals=1)
    final=df_final.to_json(orient='records')
    return {"preditedValues":final}


@app.post("/uploadFilePred",tags=['Prediction Upload Controller'])
def upload_file(parent:str, child:str,model: str,file: UploadFile = File(...)):
       file=file.file.read()
       df=pd.read_excel(pd.io.common.BytesIO(file),sheet_name='Sheet1',engine='openpyxl')
       #df[df.columns[0]]=np.around(df[df.columns[0]])
       df.set_index('Wavelength (nm)', inplace=True)
       final_pred=upload_predict(df,parent,child,model)
       return {'prediction':final_pred}


@app.post("/uploadFile",tags=['File Upload Controller'])
def upload_file(file: UploadFile = File(...)):
   global df
   global maincolumns
   file=file.file.read()
   df=pd.read_excel(pd.io.common.BytesIO(file),sheet_name='Sheet1',engine='openpyxl')

   if '% Moisture Content' in df.columns:

       df.rename(columns = {'Wavelength (nm)' : 'Wavelength'}, inplace = True)
       df1=df
       df1=df1.drop(['% Moisture Content','% Oil Content'], axis = 1)
       df1=df1.T
       df1.columns=df1.iloc[0]
       df1 = df1.iloc[1:]
       df1=df1.reset_index()
       df1.rename(columns = {'index' : 'Wavelength (nm)'}, inplace = True)


       final_out=df.to_json(orient='records')
       final_out1=df1.to_json(orient='records')
       return {'table':final_out,'graph':final_out1}

   else:
       df[df.columns[0]]=np.around(df[df.columns[0]])
       df.set_index('Wavelength (nm)', inplace=True)
       df2=df.reset_index()
       df2 = df2.loc[:, ~df2.columns.str.contains('^Unnamed')]

       df1 = df.loc[:, ~df.columns.str.contains('^Unnamed')]

       df1=df1.T
       df1.index.names = ['Wavelength']
       df1=df1.reset_index()
       #df1.columns = np.arange(len(df1.columns))



       final_out=df2.to_json(orient='records')
       final_out1=df1.to_json(orient='records')


       return {'table':final_out1,'graph':final_out}




@app.post("/savitzkyGolay",tags=['Spectral Pretreatment Controller'])
def savitzky_golay(parentName:str, childName:str, sample:str,derivative:int =1,polynomial:int=2,window:int =5,inputf: JSONStructure = None):
    smoothed_data = savitzky_golay_f(parentName,childName,sample,derivative,polynomial,window,inputf)
    return smoothed_data


@app.get("/scanSpectralData1",tags=['Sensor Controller'])
def custom_config(parent: str, child: str, name: str,start: float,end: float, repeat: float, res: float,pattern: float,setting : str):
    nmwidth={"2.34":447,"3.51":410,"4.68":378,"5.85":351,"7.03":351,"8.20":328,"9.37":307,"10.54":289}
    filename = ""
    key = "{:.2f}".format(res)
    if setting == 'Default':
        set_scan_config(name,start,end,repeat,res,nmwidth[key])
        res=scansample(filename,name,parent,child,res,0)
        return res
    else:
        set_scan_config(name,start,end,repeat,res,nmwidth[key])
        res=scansample(filename,name,parent,child,res,0)
        input_data=res['graph']
        predict_pls(name,parent, child, setting, json.loads(input_data))
        return res

@app.get("/scanCustomSpectralData",tags=['Sensor Controller'])
def custom_config(parent: str, child: str,name: str,start: float,end: float, repeat: float, res: float, pattern: float,setting: str):
    if setting == 'Default':
        #950 1650 2.34 390,3.5,4.68,5.85,7.03,8.2,9.37,10.54
        set_scan_config(name,start,end,repeat,res,pattern)
        res=scanRef(res)
        return res

@app.get("/scanReferrenceData",tags=['Sensor Controller'])
def custom_config(name:str,start: float,end: float, repeat: float):

    #950 1650 2.34 390,3.5,4.68,5.85,7.03,8.2,9.37,10.54
    nmwidth={0:[2.34,447],1:[3.51,410],2:[4.68,378],3:[5.85,351],4:[7.03,351],5:[8.20,328],6:[9.37,307],7:[10.54,289]}
    #nmwidth={0:[7.03,351]}
    for i in list(nmwidth.keys()):
        set_scan_config(name,start,end,repeat,nmwidth[i][0],nmwidth[i][1])
        res=scanRef(nmwidth[i][0])
    res=mergeALlRef()
    return res


@app.get("/scanCustomOverlaySpectralData",tags=['Sensor Controller'])
def custom_config(parent: str, child: str,name: str,start: float,end: float, repeat: float, res: float, pattern: float):

    set_scan_config(name,start,end,repeat,res,pattern)
    res=scansample(" ",name,parent,child,res,1)
    return res

@app.get("/scanCustomOverlayMultiSpectralData",tags=['Sensor Controller'])
def custom_config(fileName: str, parent: str, child: str,name: str,start: float,end: float, repeat: float, res: float, pattern: float):
    nmwidth={"2.34":447,"3.51":410,"4.68":378,"5.85":351,"7.03":351,"8.20":328,"9.37":307,"10.54":289}
    key = "{:.2f}".format(res)
    set_scan_config(name,start,end,repeat,res,nmwidth[key])
    res=scansample(fileName,name,parent,child,res,2)
    return res

@app.get("/scanCustomOverlayAutoMultiSpectralData",tags=['Sensor Controller'])
def custom_config(stime:str,number: str ,fileName: str, parent: str, child: str,name: str,start: float,end: float, repeat: float, res: float,pattern: float):

    set_scan_config(name,start,end,repeat,res, pattern)
    res=scanoverlaymultiAutomatic(fileName,name,parent,child,res,int(stime),int(number))
    return res

@app.get("/sensorTest",tags=['Sensor Controller'])
def sensor_activate_test():
    global sensorOpen
    if sensorOpen == 0:
        setup(VID,PID)
        time.sleep(1)
        get_date()
        sensorOpen = 1
    return {"test":'ok'}

@app.get("/allModels",tags=['Model Get Controller'])
def all_models(parentName:str, childName:str):
    type = 1 # for data 1: for graphs
    files = models(parentName,childName,type)
    return {'Mlmodels':files}

@app.get("/allMetricFiles",tags=['Model Get Controller'])
def all_models_metrics(parentName:str, childName:str):
    type = 0 # 0:for data 1: for graphs
    files = models(parentName,childName,type)
    return {'Mlmodels':files}

@app.get("/metrics",tags=['Model Get Controller'])
def all_models_metrics(parentName:str, childName:str,model:str):
    with open('Models/'+parentName+'/'+childName+'/graphs/'+model+'.json') as f:
        data=json.load(f)
    return {'metrics':data}

@app.get("/userValidation",tags=['Authentication Controller'])
def user_validate(userName: str, password: str):
    if not os.path.isdir('Models'):
        os.makedirs('Models')
    authenticatedUSer=Auth(userName,password)
    authenticatedUSer=authenticatedUSer.login()
    return authenticatedUSer
