# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 13:02:52 2020

@author: rajesh
"""


from Setup import *
from Format_data import *
from Pretreatment import *
from Nirsensor import *
from Sensor.usb_comm import *
from NIR_Software.authentication.auth import Auth
from NIR_Software.sensor.scan import Scan
from Analysis import *
from Models import *




app = FastAPI(title="NIR Spectroscopy",debug = True)


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

JSONObject = Dict[AnyStr, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject]

if __name__ == '__main__':
    uvicorn.run("main:app",host="0.0.0.0",workers=1,port=8000)

#**********************************************************************************************
#-------------------------------Logging Functions-----------------------------------------
#**********************************************************************************************
class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentaion.
    See https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

def format_record(record: dict) -> str:
    """
    Custom format for loguru loggers.
    Uses pformat for log any data like request/response body during debug.
    Works with logging if loguru handler it.
    """
    format_string = LOGURU_FORMAT

    if record["extra"].get("payload") is not None:
        record["extra"]["payload"] = pformat(
            record["extra"]["payload"], indent=4, compact=True, width=88
        )
        format_string += "\n<level>{extra[payload]}</level>"

    format_string += "{exception}\n"
    return format_string

# set loguru format for root logger
logging.getLogger().handlers = [InterceptHandler()]
logger.configure(handlers=[{"sink": "logger.txt", "level": logging.DEBUG, "format": format_record}])
logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]


@app.get("/")
def index(request: Request) -> None:
    logger.info("loguru log")
    logging.info("logging log")

    logging.getLogger("fastapi").debug("fatapi info log")
    logger.bind(payload=dict(request.query_params)).debug("params with formating")
    return None


#**********************************************************************************************
#-------------------------------PreTreatment Functions-----------------------------------------
#**********************************************************************************************
@app.post("/SNV",tags=['Transform Algorithms'])
def tr_algo_sn(parentName:str, childName:str, sample:str, inputf: JSONStructure = None):
        SNV = snv()
        final_out,final_out_table = PT_scatter_correction(parentName, childName, sample,SNV,'T_SNV', inputf)
        return {'snv':final_out,'table':final_out_table}

@app.post("/MSC",tags=['Transform Algorithms'])
def tr_algo_msc(parentName:str, childName:str, sample:str, inputf: JSONStructure = None):
        MSC = msc()
        final_out,final_out_table = PT_scatter_correction(parentName, childName, sample,MSC,'T_MSC', inputf)
        return {'msc':final_out,'table':final_out_table}


@app.post("/savitzkyGolay",tags=['Spectral Pretreatment Controller'])
def savitzky_golay(parentName:str, childName:str, sample:str,derivative:int =2,polynomial:int=2,window:int =11,inputf: JSONStructure = None):
    smoothed_data = PT_savitzky_golay(parentName,childName,sample,derivative,polynomial,window,inputf)
    return smoothed_data

#**********************************************************************************************
#-------------------------------ML Functions-----------------------------------------
#**********************************************************************************************

@app.post('/plsAlgoritm',tags=['Ml Algorithms'])
def PLS_Algorithm(parentName:str,childName:str,sample: str,scatterCorrection: str,window: int,ploynomial: int,derivative: int, inputf: JSONStructure = None):

   parameters = ['% Moisture Content','% Fat Content', '% Protein Content']
   final_data = pls_func(parentName,childName,sample,scatterCorrection, \
   window,ploynomial,derivative,inputf,parameters)

   return final_data

#**********************************************************************************************
#-------------------------------File Upload Functions-----------------------------------------
#**********************************************************************************************

def read_file(file):

    file=file.file.read()
    try:
        df=pd.read_excel(pd.io.common.BytesIO(file),sheet_name='Sheet1',engine='openpyxl')
    except:
        df=pd.read_csv(pd.io.common.BytesIO(file))

    return df

@app.post("/uploadFilePred",tags=['Prediction Upload Controller'])
def upload_file(parent:str, child:str,model: str,file: UploadFile = File(...)):

    df = read_file(file)
    df = FD_format_data(df)                                                          # Clean data

    final_pred=AN_upload_predict(child,parent,child,model,df)
    return {'prediction':final_pred}


@app.post("/uploadFile",tags=['File Upload Controller'])
def upload_file(file: UploadFile = File(...)):
    parameters = ['% Moisture Content','% Fat Content', '% Protein Content']
    df = read_file(file)

    if '% Moisture Content' in df.columns:

        df = FD_format_data(df)

        y_param_columns = df[parameters]
        final_param=y_param_columns.copy()                                      # Copy prediction parameter values
        final_param=final_param.to_json(orient='records')

        df1 = df.drop(parameters, axis = 1)                                     # drop prediction parameters
        df1 = FD_Transpose_data(df1)
        final_graph=df1.to_json(orient='records')

        df.reset_index(inplace = True)
        final_table=df.to_json(orient='records')                                # Convert to json

        return {'table':final_table,'graph':final_graph,'parameters':final_param}


#**********************************************************************************************
#-------------------------------Sensor Functions-----------------------------------------
#**********************************************************************************************

@app.get("/scanSpectralData1",tags=['Sensor Controller'])
def custom_config(parent: str, child: str, name: str,start: float,end: float, repeat: float, res: float,pattern: float,setting : str):
    #nmwidth={"2.34":447,"3.51":410,"4.68":378,"5.85":351,"7.03":351,"8.20":328,"9.37":307,"10.54":289}
    filename = ""
    #key = "{:.2f}".format(res)
    #set_scan_config(name,start,end,repeat,res,nmwidth[key])

    result=NS_scansample(filename,name,parent,child,res,0)
    if setting != 'Default':
        input_data = json.loads(result['graph'])
        data = pd.DataFrame(input_data)
        data = FD_format_data(data)
        data = FD_Transpose_data(data)
        data.set_index('Wavelength (nm)', inplace=True)                         # Set wavelength column as index
        AN_upload_predict(name,parent, child, setting,data)
    return result

@app.get("/scanCustomSpectralData",tags=['Sensor Controller'])
def custom_config(parent: str, child: str,name: str,start: float,end: float, repeat: float, res: float, pattern: float,setting: str):
    if setting == 'Default':
        #950 1650 2.34 390,3.5,4.68,5.85,7.03,8.2,9.37,10.54
        #set_scan_config(name,start,end,repeat,res,pattern)

        res=NS_scanRef(res)
        return res

@app.get("/scanReferrenceData",tags=['Sensor Controller'])
def custom_config(name:str,start: float,end: float, repeat: float):

    #950 1650 2.34 390,3.5,4.68,5.85,7.03,8.2,9.37,10.54
    nmwidth={0:[2.34,444],1:[3.51,407],2:[4.68,378],3:[5.85,350],4:[7.03,350],5:[8.20,327],6:[9.37,306],7:[10.54,288]}
    for i in list(nmwidth.keys()):
        #set_scan_config(name,start,end,repeat,nmwidth[i][0],nmwidth[i][1])
        res=NS_scanRef(nmwidth[i][0])
    res=NS_mergeALlRef()
    return res


@app.get("/scanCustomOverlaySpectralData",tags=['Sensor Controller'])
def custom_config(parent: str, child: str,name: str,start: float,end: float, repeat: float, res: float, pattern: float):

    #set_scan_config(name,start,end,repeat,res,pattern)
    res=NS_scansample(" ",name,parent,child,res,1)
    return res

@app.get("/scanCustomOverlayMultiSpectralData",tags=['Sensor Controller'])
def custom_config(fileName: str, parent: str, child: str,name: str,start: float,end: float, repeat: float, res: float, pattern: float):
    #nmwidth={"2.34":447,"3.51":410,"4.68":378,"5.85":351,"7.03":351,"8.20":328,"9.37":307,"10.54":289}
    #key = "{:.2f}".format(res)
    #set_scan_config(name,start,end,repeat,res,nmwidth[key])
    res=NS_scansample(fileName,name,parent,child,res,2)
    return res

@app.get("/scanCustomOverlayAutoMultiSpectralData",tags=['Sensor Controller'])
def custom_config(stime:str,number: str ,fileName: str, parent: str, child: str,name: str,start: float,end: float, repeat: float, res: float,pattern: float):
    #set_scan_config(name,start,end,repeat,res, pattern)
    res=NS_scanoverlaymultiAutomatic(fileName,name,parent,child,res,int(stime),int(number))
    return res

@app.get("/sensorTest",tags=['Sensor Controller'])
def sensor_activate_test():
    global sensorOpen
    logger.info("SensorConnected")
    if sensorOpen == 0:
        setup(VID,PID)
        time.sleep(1)
        get_date()
        sensorOpen = 1
    return {"test":'ok'}

#**********************************************************************************************
#-------------------------------Models Functions-----------------------------------------
#**********************************************************************************************

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

#**********************************************************************************************
#-------------------------------Authentication Functions-----------------------------------------
#**********************************************************************************************

@app.get("/userValidation",tags=['Authentication Controller'])
def user_validate(userName: str, password: str):
    if not os.path.isdir('Models'):
        os.makedirs('Models')
    authenticatedUSer=Auth(userName,password)
    authenticatedUSer=authenticatedUSer.login()
    return authenticatedUSer
#**********************************************************************************************
#-------------------------------Fetch json Functions-----------------------------------------
#**********************************************************************************************

@app.get("/parameters",tags=['Fetch Data'])
def get_parameters():
    return PM_parameters()

@app.get("/categories",tags=['Fetch Data'])
def get_categories():
    return PM_categories()
