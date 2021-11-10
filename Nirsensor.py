# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 13:02:52 2020

@author: rajesh
"""


from Setup import *

def scan(res):

    get_scan_config_id()

    start_scan(0) # donot store in sd card

    results = get_results() # get scan results
    ref_scan = get_ref_data() # get reference values

    # Convert the results into a dataframe

    values = {"Wavelength (nm)":results["wavelength"],"intensity":results["intensity"],"reference":ref_scan["intensity"]}
    df = pd.DataFrame(values)
    df = df[0:results["length"]]
    df.loc[df.intensity > 0, "reflectance"] = df['intensity']/df['reference'] #reflectance = sample/reference
    df['absorption'] = -(np.log10(df['reflectance']))#absorption = -log(reflectance)

    df.to_csv("referrence/ref"+str(res)+".csv")
    df[df.columns[0]]=np.around(df[df.columns[0]])
    df[df.columns[1]]=np.around(df[df.columns[1]],decimals = 5)
    df=df.dropna()
    df=df[["Wavelength (nm)","absorption","reflectance"]]
    df=df[:444]
    df1=df.T.reset_index()
    df1.columns = np.arange(len(df1.columns))
    final_out=df.to_json(orient='records')
    final_out1=df1.to_json(orient='records')


    return {"graph":final_out}


def scansam(name,parent,child,res):
    pathsam='sample/'+parent+'/'+child+'/'
    patho='overlay/'+parent+'/'+child+'/'

    get_scan_config_id()

    start_scan(0) # donot store in sd card

    results = get_results() # get scan results
    ref_scan = get_ref_data() # get reference values
    date=datetime.datetime.now().date()
    date=str(date)


    # Convert the results into a dataframe
    #df1=pd.read_csv('Referrence/'+parent+'/'+child+'/ref'+str(res)+'.csv')


    values = {"Wavelength (nm)":results["wavelength"],"intensity":results["intensity"],"reference":ref_scan["intensity"]}
    df = pd.DataFrame(values)
    df = df[0:results["length"]]
    #df['reference']=df1['intensity']

    df.loc[df.intensity > 0, "reflectance"] = df['intensity']/df['reference'] #reflectance = sample/reference
    df[name] = -(np.log10(df['reflectance']))                                 #absorption = -log(reflectance)



    df[df.columns[0]]=np.around(df[df.columns[0]])
    df[df.columns[1]]=np.around(df[df.columns[1]],decimals = 5)
    df=df.dropna()
    df=df[["Wavelength (nm)",name]]
    df=df[:444]
    print(df.shape[0])

    if os.path.isdir(pathsam+date):
        print('exists')
    else:
        os.makedirs(pathsam+date)
    df.to_csv("sample/"+parent+"/"+child+"/"+str(date)+"/"+name+'_'+str(datetime.datetime.now())+'_'+str(res)+".csv")

    if os.path.isdir(patho+date):
        print('exists')
    else:
        os.makedirs(patho+date)

    fileNameo="overlay/"+parent+"/"+child+"/"+str(date)+"/"+name+'_'+str(datetime.datetime.now())+'_'+str(res)+".csv"
    df.to_csv(fileNameo,index=False)

    df1=df.T.reset_index()
    df1.columns = np.arange(len(df1.columns))
    final_out=df.to_json(orient='records')
    final_out1=df1.to_json(orient='records')

    return {'fileName':fileNameo,'resolution':res,'table':final_out1,'graph':final_out}

def scanoverlay(name,parent,child,res):
    pathsam='overlay/'+parent+'/'+child+'/'
    get_scan_config_id()

    start_scan(0) # donot store in sd card

    results = get_results() # get scan results
    ref_scan = get_ref_data() # get reference values
    date=datetime.datetime.now().date()
    date=str(date)


    # Convert the results into a dataframe
    df1=pd.read_csv('Referrence/'+parent+'/'+child+'/ref'+str(res)+'.csv')


    values = {"Wavelength (nm)":results["wavelength"],"intensity":results["intensity"],"reference":ref_scan["intensity"]}
    df = pd.DataFrame(values)
    df = df[0:results["length"]]
    df['reference']=df1['intensity']

    df.loc[df.intensity > 0, "reflectance"] = df['intensity']/df['reference'] #reflectance = sample/reference
    df['absorption'] = -(np.log10(df['reflectance']))#absorption = -log(reflectance)
    df=df[["Wavelength (nm)","absorption"]]

    if os.path.isdir(pathsam+date):
        print('exists')
    else:
        os.mkdir(pathsam+date)

    fileName="overlay/"+parent+"/"+child+"/"+str(date)+"/"+name+'_'+str(datetime.datetime.now())+'_'+str(res)+".csv"
    df.to_csv(fileName,index=False)



    df[df.columns[0]]=np.around(df[df.columns[0]])
    df[df.columns[1]]=np.around(df[df.columns[1]],decimals = 5)
    df=df.dropna()
    df=df[["Wavelength (nm)","absorption"]]
    df=df[:444]
    df1=df.T.reset_index()
    df1.columns = np.arange(len(df1.columns))
    final_out=df.to_json(orient='records')
    final_out1=df1.to_json(orient='records')

    return {'fileName':fileName,'resolution':res,'table':final_out1,'graph':final_out}


def scanoverlaymultiAutomatic(fileName,name,parent,child,res,stime,number):
    print(fileName)
    pathsam='overlay/'+parent+'/'+child+'/'

    for i in range(1,number+1):
        df1=pd.read_csv('Referrence/'+parent+'/'+child+'/ref'+str(res)+'.csv')

        time.sleep(5)

        get_scan_config_id()

        start_scan(0) # donot store in sd card

        results = get_results() # get scan results
        ref_scan = get_ref_data() # get reference values
        date=datetime.datetime.now().date()
        date=str(date)


        # Convert the results into a dataframe


        values = {"Wavelength (nm)":results["wavelength"],"intensity":results["intensity"],"reference":ref_scan["intensity"]}
        df = pd.DataFrame(values)
        df = df[0:results["length"]]
        df['reference']=df1['intensity']

        df.loc[df.intensity > 0, "reflectance"] = df['intensity']/df['reference'] #reflectance = sample/reference
        df['absorption'] = -(np.log10(df['reflectance']))#absorption = -log(reflectance)
        df_final=pd.read_csv(fileName)

        colName=name+'_'+str(i)
        df_final[colName]=df['absorption']
        df_final.to_csv(fileName,index=False)
        df[df.columns[0]]=np.around(df[df.columns[0]])
        df[df.columns[1]]=np.around(df[df.columns[1]],decimals = 5)
        df=df.dropna()
        df=df[["Wavelength (nm)","absorption"]]
        df=df[:444]
        df1=df.T.reset_index()
        df1.columns = np.arange(len(df1.columns))
    final_out=df_final.to_json(orient='records')
    final_out1=df1.to_json(orient='records')

    return {'fileName':fileName,'resolution':res,'table':final_out1,'graph':final_out}


def scanoverlaymulti(fileName,name,parent,child,res):
    pathsam='overlay/'+parent+'/'+child+'/'
    get_scan_config_id()

    start_scan(0) # donot store in sd card

    results = get_results() # get scan results
    ref_scan = get_ref_data() # get reference values
    date=datetime.datetime.now().date()
    date=str(date)


    # Convert the results into a dataframe
    df1=pd.read_csv('Referrence/'+parent+'/'+child+'/ref'+str(res)+'.csv')


    values = {"Wavelength (nm)":results["wavelength"],"intensity":results["intensity"],"reference":ref_scan["intensity"]}
    df = pd.DataFrame(values)
    df = df[0:results["length"]]
    df['reference']=df1['intensity']

    df.loc[df.intensity > 0, "reflectance"] = df['intensity']/df['reference'] #reflectance = sample/reference
    df['absorption'] = -(np.log10(df['reflectance']))#absorption = -log(reflectance)
    df_final=pd.read_csv(fileName)


    df_final[name]=df['absorption']
    df_final.to_csv(fileName,index=False)
    df[df.columns[0]]=np.around(df[df.columns[0]])
    df[df.columns[1]]=np.around(df[df.columns[1]],decimals = 5)
    df=df.dropna()
    df=df[["Wavelength (nm)","absorption"]]
    df=df[:444]
    df1=df.T.reset_index()
    df1.columns = np.arange(len(df1.columns))
    final_out=df_final.to_json(orient='records')
    final_out1=df1.to_json(orient='records')

    return {'fileName':fileName,'resolution':res,'table':final_out1,'graph':final_out}



def activate_sensor(ref):

    set_active_config(0)
    get_scan_config_id()
    start_scan(0) # donot store in sd card

    results = get_results() # of scanData
    print(results)

    time.sleep(1)

    ref_scan = get_ref_data()
    # Convert the results into a dataframe
    if ref == 1:
        refdf=pd.read_csv('sample.csv')

    values = {"Wavelength (nm)":results["wavelength"],"intensity":results["intensity"],"reference":ref_scan["intensity"]}
    df = pd.DataFrame(values)
    df = df[(df[['Wavelength (nm)','intensity']] > 0).all(axis=1)].reset_index() # drop values of 0 or less
    df.to_csv('sample1.csv')

    df['reflectance'] = df['intensity']/df['reference'] #reflectance = sample/reference
    df['absorption'] = -(np.log10(df['reflectance']))#absorption = -log(reflectance)
    if ref == 1:
        df['ref']=refdf['reference']
    df=df.drop(['index','reflectance','intensity','reference'],axis=1)
    print(df)
    df[df.columns[0]]=np.around(df[df.columns[0]])
    df[df.columns[1]]=np.around(df[df.columns[1]],decimals = 5)
    df=df.dropna()
    df=df[:444]
    df1=df.T.reset_index()
    df1.columns = np.arange(len(df1.columns))
    final_out=df.to_json(orient='records')
    final_out1=df1.to_json(orient='records')

    return {'table':final_out1,'graph':final_out}
"""
def scanRef():


    get_scan_config_id()

    start_scan(0) # donot store in sd card

    results = get_results() # get scan results
    ref_scan = get_ref_data() # get reference values
    date=datetime.datetime.now().date()
    date=str(date)


    # Convert the results into a dataframe
    values = {"Wavelength (nm)":results["wavelength"],"intensity":results["intensity"],"reference":ref_scan["intensity"]}
    df = pd.DataFrame(values)
    df = df[0:results["length"]]


    df.loc[df.intensity > 0, "reflectance"] = df['intensity']/df['reference'] #reflectance = sample/reference
    df[name] = -(np.log10(df['reflectance']))                                 #absorption = -log(reflectance)

    if os.path.isdir(pathsam+date):
        print('exists')
    else:
        os.mkdir(pathsam+date)
    df.to_csv("sample/"+parent+"/"+child+"/"+str(date)+"/"+name+'_'+str(datetime.datetime.now())+'_'+str(res)+".csv")



    return {'Success':'True'}
"""

def mergeALlRef():


    path = 'referrence/'
    extension = 'csv'
    os.chdir(path)
    result = glob.glob('*.{}'.format(extension))

    df1=pd.DataFrame()
    df=pd.read_csv('ref2.34.csv')
    df1['Wavelength (nm)']=df['Wavelength (nm)']


    for i in result:
        colname=i.split('ref')[1][:-4]
        df=pd.read_csv(i)
        df=df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df1[colname]=df['absorption']
    final_out=df1.to_json(orient='records')
    return {'table':final_out}
