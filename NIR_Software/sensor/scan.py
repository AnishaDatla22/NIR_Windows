from NIR_Software.application_logging import logger
import os
#from Setup import *


class Scan:
    def __init__(self,name,parent,child,res):
        self.name=name
        self.parent=parent
        self.child=child
        self.res=res
        self.file_object = open("NIR_Software/authentication/Authenticatedusers.txt", 'a+')
        self.log_writer = logger.App_Logger()
    def scanoverlaymultiAutomatic(self,fileName,stime,number):
        print(fileName)
        pathsam='overlay/'+self.parent+'/'+self.child+'/'

        for i in range(1,number+1):
            df1=pd.read_csv('Referrence/'+self.parent+'/'+self.child+'/ref'+str(self.res)+'.csv')

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

        return {'fileName':fileName,'resolution':self.res,'table':final_out1,'graph':final_out}


    def scanoverlaymulti(self,fileName):
        pathsam='overlay/'+self.parent+'/'+self.child+'/'
        get_scan_config_id()

        start_scan(0) # donot store in sd card

        results = get_results() # get scan results
        ref_scan = get_ref_data() # get reference values
        date=datetime.datetime.now().date()
        date=str(date)


        # Convert the results into a dataframe
        df1=pd.read_csv('Referrence/'+self.parent+'/'+self.child+'/ref'+str(self.res)+'.csv')


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

        return {'fileName':fileName,'resolution':self.res,'table':final_out1,'graph':final_out}


    def scanoverlay(self):
        pathsam='overlay/'+self.parent+'/'+self.child+'/'
        get_scan_config_id()

        start_scan(0) # donot store in sd card

        results = get_results() # get scan results
        ref_scan = get_ref_data() # get reference values
        date=datetime.datetime.now().date()
        date=str(date)


        # Convert the results into a dataframe
        df1=pd.read_csv('Referrence/'+self.parent+'/'+self.child+'/ref'+str(self.res)+'.csv')


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

        fileName="overlay/"+self.parent+"/"+self.child+"/"+str(date)+"/"+self.name+'_'+str(datetime.datetime.now())+'_'+str(self.res)+".csv"
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

        return {'fileName':fileName,'resolution':self.res,'table':final_out1,'graph':final_out}


    def scanReferrence(self):

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

        df.to_csv("Referrence/"+self.parent+"/"+self.child+"/ref"+str(self.res)+".csv")
        df[df.columns[0]]=np.around(df[df.columns[0]])
        df[df.columns[1]]=np.around(df[df.columns[1]],decimals = 5)
        df=df.dropna()
        df=df[["Wavelength (nm)","absorption","reflectance"]]
        df=df[:444]
        df1=df.T.reset_index()
        df1.columns = np.arange(len(df1.columns))
        final_out=df.to_json(orient='records')
        final_out1=df1.to_json(orient='records')

        return {'table':final_out1,'graph':final_out}
    def scanSample(self):
        pathsam='sample/'+self.parent+'/'+self.child+'/'
        patho='overlay/'+self.parent+'/'+self.child+'/'

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
        df[self.name] = -(np.log10(df['reflectance']))                                 #absorption = -log(reflectance)



        df[df.columns[0]]=np.around(df[df.columns[0]])
        df[df.columns[1]]=np.around(df[df.columns[1]],decimals = 5)
        df=df.dropna()
        df=df[["Wavelength (nm)",self.name]]
        df=df[:444]
        print(df.shape[0])

        if os.path.isdir(pathsam+date):
            print('exists')
        else:
            os.makedirs(pathsam+date)
        df.to_csv("sample/"+self.parent+"/"+self.child+"/"+str(date)+"/"+self.name+'_'+str(datetime.datetime.now())+'_'+str(self.res)+".csv")

        if os.path.isdir(patho+date):
            print('exists')
        else:
            os.makedirs(patho+date)

        fileNameo="overlay/"+self.parent+"/"+self.child+"/"+str(date)+"/"+self.name+'_'+str(datetime.datetime.now())+'_'+str(self.res)+".csv"
        df.to_csv(fileNameo,index=False)

        df1=df.T.reset_index()
        df1.columns = np.arange(len(df1.columns))
        final_out=df.to_json(orient='records')
        final_out1=df1.to_json(orient='records')

        return {'fileName':fileNameo,'resolution':self.res,'table':final_out1,'graph':final_out}
