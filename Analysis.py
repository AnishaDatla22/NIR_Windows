# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 13:02:52 2020

@author: Anisha
"""


from Setup import *
from Format_data import *

#**********************************************************************************************
#-------------------------------Prediction Functions-----------------------------------------
#**********************************************************************************************
def an_predict_flow(df,parent,child,saved_model):



    df = FD_Transpose_data(df)
    df.set_index('Wavelength (nm)', inplace=True)
    print(df)

   #Scatter Correction Check SNV or MSC
    file_path = 'Models/'+parent+'/'+child
    file_name_sc = file_path + '/scatter_correction/'+saved_model.rsplit('_', 1)[0]
    try:
        with open(file_name_sc+'_SNV.pkl', 'rb') as file:
            SC=pickle.load(file)
    except:
        with open(file_name_sc+'_MSC.pkl', 'rb') as file:
            SC=pickle.load(file)                   # SNV or MSC
    Xscatter=SC.fit_transform(df)
    print(Xscatter)

   # Pretreatment
    file_name_pt = file_path + '/pretreatment/'+saved_model.rsplit('_', 1)[0]+'_SG.pkl'
    with open(file_name_pt, 'rb') as file:
        sg_param=pickle.load(file)
    Spectra = Xscatter.values
    Xsv = signal.savgol_filter(Spectra,sg_param[0],polyorder = sg_param[1],deriv=sg_param[2],axis=0)
    df_Xsv = Xsv.T

    # Regression
    with open(file_path +'/'+saved_model+'.pkl', 'rb') as file:
        pls=pickle.load(file)
        yhat=pls.predict(df_Xsv)
    return yhat


def AN_upload_predict(name,parent,child,saved_model,input_data):

       samples=input_data.index.values.tolist()

       yhat = an_predict_flow(input_data,parent,child,saved_model)


       pred=list(yhat)
       df_pred=pd.DataFrame()
       df_pred['samples']=samples

       df_pred['prediction']=pred
       df_pred[['moisture_predict','fat_predict','protein_predict']] = pd.DataFrame(df_pred.prediction.tolist(), index= df_pred.index)
       df_pred=df_pred.round(2)
       df_pred=df_pred.drop('prediction',axis=1)

       file_path = "Models/"+parent+"/"+child+"/"
       file_name = df_pred['samples'].iloc[0]+"_prediction.csv"
       df_pred.to_csv(file_path+file_name)

       final_pred=df_pred.to_json(orient='records')
       return final_pred

#**********************************************************************************************
#-------------------------------PLS Model Building Functions----------------------------------
#**********************************************************************************************
def an_pls_actvspred(y,y_c,parameters):

    df_train_pred=pd.DataFrame()
    param_actual = []
    param_predict = []
    for param in parameters:
        param_actual.append(param + "_actual")
        param_predict.append(param + "_predict")


    train_pred=list(y_c)
    train_actual=list(y)
    df_train_pred['actual']=train_actual
    df_train_pred['prediction']=train_pred
    df_train_pred[param_actual] = pd.DataFrame(df_train_pred.actual.tolist(), index= df_train_pred.index)
    df_train_pred[param_predict] = pd.DataFrame(df_train_pred.prediction.tolist(), index= df_train_pred.index)
    df_train_pred=df_train_pred.drop(['actual','prediction'], axis = 1)
    df_train_pred=df_train_pred.round(1)
    df_pred = df_train_pred.tail(5)
    df_train_pred['Wavelength (nm)']=pd.DataFrame(np.arange(0,len(train_pred)))

    return df_train_pred, df_pred

def an_pls_regression(x_final,y,Model_path,sample_name,parameters):


    mse = []
    component = np.arange(1, MAX_PLS_COMPONENTS)
    for i in component:
        pls = PLSRegression(n_components=i)
        # Cross-validation
        y_cv = cross_val_predict(pls, x_final, y, cv=10)
        mse.append(mean_squared_error(y, y_cv))

    # Calculate and print the position of minimum in MSE
    msemin = np.argmin(mse)

    print("Suggested number of components: ", msemin+1)
    slcolumns=[]
    for i in range(1,msemin+2):
        slcolumns.append('PC'+str(i))

    mse_df=pd.DataFrame(mse)
    mse_df['Wavelength (nm)']=pd.DataFrame(np.arange(0,len(mse)))
    mse_df.columns=['MSE','Wavelength (nm)']
    mse_df=mse_df.round({"MSE":3})
    mse_df = mse_df.astype({"MSE": float})


    # Define PLS object with optimal number of components
    pls_opt = PLSRegression(n_components=msemin+1)
    pls_opt.fit(x_final, y)
    y_c = pls_opt.predict(x_final)

    dump(pls_opt, open(Model_path+"/"+sample_name+'_plsmodel.pkl', 'wb'))

    loadings_df=pd.DataFrame(pls_opt.x_loadings_,columns=slcolumns)
    loadings_df['Wavelength (nm)']=pd.DataFrame(np.arange(0,len(pls_opt.x_loadings_)))

    scores_df=pd.DataFrame(pls_opt.x_scores_,columns=slcolumns)
    scores_df = scores_df.rename(columns={'PC1': 'Wavelength (nm)'})


    # Cross-validation
    df_train_pred,df_pred = an_pls_actvspred(y,y_c,parameters)



    y_cv = cross_val_predict(pls_opt, x_final, y, cv=10)
    # Calculate scores for calibration and cross-validation
    r2_c = r2_score(y, y_c,multioutput='raw_values')
    r2_c_r = [round(score,2) for score in r2_c]
    r2_cv = r2_score(y, y_cv,multioutput='raw_values')
    r2_cv_r = [round(score,2) for score in r2_cv]
    r2_c_test=r2_score(y[-5:], y_cv[-5:],multioutput='raw_values')
    r2_c_test_r = [round(score,2)for score in r2_c_test]

    # Calculate mean squared error for calibration and cross validation
    mse_c = mean_squared_error(y, y_c)
    mse_cv = mean_squared_error(y, y_cv)
    mse_c_test = mean_squared_error(y[-5:], y_c[-5:])

    rmse_c = mean_squared_error(y, y_c,multioutput='raw_values',squared=False)
    rmse_cv = mean_squared_error(y, y_cv,multioutput='raw_values',squared=False)
    rmse_c_test = mean_squared_error(y[-5:], y_c[-5:],multioutput='raw_values',squared=False)
    rmse_c_r = [round(rmse,2) for rmse in rmse_c]
    rmse_cv_r = [round(rmse,2) for rmse in rmse_cv]
    rmse_c_test_r = [round(rmse,2) for rmse in rmse_c_test]


    final_mse=mse_df.to_json(orient='records')
    final_pred=df_pred.to_json(orient='records')
    final_loadings=loadings_df.to_json(orient='records')
    final_scores=scores_df.to_json(orient='records')
    final_train=df_train_pred.to_json(orient='records')


    final_data = {'train':final_train,'scores':final_scores,'loadings':final_loadings,
                   'prediction':final_pred,'mse':final_mse,'R2_calib':r2_c_r,
                   'R2_cv':r2_cv_r,'MSE_calib':round(mse_c, 2),'MSE_cv':round(mse_cv, 2),
                   'R2_calib_pred':r2_c_test_r,'MSE_calib_pred':round(mse_c_test, 2),
                   'RMSE_calib':rmse_c_r,'RMSE_cv':rmse_cv_r,'RMSE_calib_pred':rmse_c_test_r}

    return final_data

def AN_pls_algo(parent,child,sample_name,scatterCorrection,window,polynomial,derivative,input_file,parameters):


    param=pd.DataFrame(input_file)
    try:
       y=param[parameters].values
    except:
       print("Selected Parameters are not present in the file")

    Model_path = "Models/"+parent+"/"+child
    file_name = Model_path +"/pretreatment/"+ sample_name + "_SG.csv"
    if not os.path.exists(Model_path):
         os.makedirs(Model_path)
    if not os.path.exists(Model_path+'/graphs/'):
         os.makedirs(Model_path+'/graphs/')

    try:
        x =pd.read_csv(file_name)
        x=x.set_index('Wavelength (nm)')
        x_final=x.values
    except:
        print("Error no pretreatment file")

    final_data = an_pls_regression(x_final,y,Model_path,sample_name,parameters)

    file_name = Model_path+'/graphs/'+sample_name + "_plsmodel.json"
    json_object = json.dumps(final_data, indent = 4)



    with open(file_name,'w') as f:
        f.write(json_object)

    return final_data
