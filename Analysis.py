# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 13:02:52 2020

@author: rajesh
"""


from Setup import *


def predict_pls(name,parent,child,saved_model, input_data):

    df=pd.DataFrame(input_data)
    df=df.set_index('Wavelength (nm)')
    df = df.loc[:,~df.columns.str.match("Unnamed")]


    with open('Models/'+parent+'/'+child+'/scatter_correction/'+saved_model.rsplit('_', 1)[0]+'_snv.pkl', 'rb') as file:
        SNV=pickle.load(file)

    Xscatter=SNV.fit_transform(df)

    Xscatter= Xscatter.T

    with open('Models/'+parent+'/'+child+'/pretreatment/'+saved_model.rsplit('_', 1)[0]+'_svgolay.pkl', 'rb') as file:
        sg_param=pickle.load(file)
    Xsv = signal.savgol_filter(Xscatter, sg_param[0], polyorder = sg_param[1],deriv=sg_param[2])

    with open('Models/'+parent+'/'+child+'/'+saved_model+'.pkl', 'rb') as file:
        pls=pickle.load(file)

    yhat=pls.predict(Xsv)
    #print(yhat)

    predict_dict = {}

    predict_dict['Predicted Data'] = yhat.tolist()


    json_fmt = json.dumps(predict_dict,indent=4)
    return json_fmt

def predict_flow(df,parent,child,saved_model):

    #Scatter Correction
    file_path = 'Models/'+parent+'/'+child
    file_name_sc = file_path + '/scatter_correction/'+saved_model.rsplit('_', 1)[0]+'_snv.pkl'
    df = df.dropna()

    if not os.path.exists(file_name_sc):
        Xscatter = df
    else:
        with open(file_name_sc, 'rb') as file:
            SC=pickle.load(file)                   # SNV or MSC
        Xscatter=SC.fit_transform(df)
        #Xscatter = Xscatter.loc[:, ~Xscatter.columns.str.contains('^Unnamed')]
    Xscatter= Xscatter.T

   # Pretreatment
    file_name_pt = file_path + '/pretreatment/'+saved_model.rsplit('_', 1)[0]+'_svgolay.pkl'

    if not os.path.exists(file_name_pt):
        Xsv = df.T
    else:
        with open(file_name_pt, 'rb') as file:
            sg_param=pickle.load(file)
        Xsv = signal.savgol_filter(df,sg_param[0],polyorder = sg_param[1],deriv=sg_param[2])

    # Regression
    with open(file_path +'/'+saved_model+'.pkl', 'rb') as file:
        pls=pickle.load(file)
    yhat=pls.predict(Xsv)

    return yhat

def pls_func(parent,child,sample_name,scatterCorrection,window,polynomial,derivative,input_file):


    df=pd.DataFrame(input_file)
    #df = pd.read_excel(input_file,index_col=0,engine='openpyxl')
    SNV=snv()
    MSC=msc()
    df=df.fillna(df.mean())

    y=df[['% Moisture Content','% Fat Content', '% Protein Content']].values
    x=df.drop(['% Moisture Content','% Fat Content', '% Protein Content'], axis=1)

    x=x.set_index('Wavelength')
    x1=x.T

    file_path = "Models/"+parent+"/"+child+"/"
    if not os.path.exists(file_path +"scatter_correction/"):
        os.makedirs(file_path +"scatter_correction/")
    if not os.path.exists(file_path +"pretreatment/"):
        os.makedirs(file_path + "pretreatment/")


    if scatterCorrection == 'SNV':
        dump(SNV, open(file_path +'scatter_correction/'+sample_name+'_snv.pkl', 'wb'))
        x_scatter=SNV.fit_transform(x1)
    elif scatterCorrection == 'MSC':
        dump(MSC, open(file_path+'scatter_correction/'+sample_name+'_msc.pkl', 'wb'))

        x_scatter=MSC.fit_transform(x1)


    Xpt = signal.savgol_filter(x_scatter, window, polynomial, deriv=derivative)
    sav_gol_param = [window,polynomial,derivative]

    dump(sav_gol_param,open(file_path+'pretreatment/'+sample_name+'_svgolay.pkl', 'wb'))
    x_final=Xpt.T


    mse = []
    component = np.arange(1, 13)
    for i in component:
        pls = PLSRegression(n_components=i)
        # Cross-validation
        y_cv = cross_val_predict(pls, x_final, y, cv=10)
        mse.append(mean_squared_error(y, y_cv))
        comp = 100*(5+1)/40
        # Trick to update status on the same line

    # Calculate and print the position of minimum in MSE
    msemin = np.argmin(mse)

    print("Suggested number of components: ", msemin+1)
    slcolumns=[]
    for i in range(1,msemin+2):
        slcolumns.append('F'+str(i))

    mse_df=pd.DataFrame(mse)
    mse_df['Wavelength (nm)']=pd.DataFrame(np.arange(0,len(mse)))

    mse_df.columns=['MSE','Wavelength (nm)']
    mse_df=mse_df.round({"MSE":3})
    mse_df = mse_df.astype({"MSE": float})
    # Define PLS object with optimal number of components
    pls_opt = PLSRegression(n_components=msemin+1)
    pls_opt.fit(x_final, y)

    dump(pls_opt, open(file_path +sample_name+'_plsmodel.pkl', 'wb'))

    # Fir to the entire dataset

    y_c = pls_opt.predict(x_final)
    loadings_df=pd.DataFrame(pls_opt.x_loadings_,columns=slcolumns)
    loadings_df['Wavelength (nm)']=pd.DataFrame(np.arange(0,len(pls_opt.x_loadings_)))
    scores_df=pd.DataFrame(pls_opt.x_scores_,columns=slcolumns)

    #scores_df=scores_df[[0:slcolumns]]
    scores_df = scores_df.rename(columns={'F1': 'Wavelength (nm)'})

    #print(scores_df)

    # Cross-validation
    print(y_c[-5:])
    pred=list(y_c[-5:])
    actual=list(y[-5:])
    df_pred=pd.DataFrame()
    df_pred['actual']=actual
    df_pred['prediction']=pred
    df_pred[['moisture_actual','fat_actual','protein_actual']] = pd.DataFrame(df_pred.actual.tolist(), index= df_pred.index)
    df_pred[['moisture_predict','fat_predict','protein_predict']] = pd.DataFrame(df_pred.prediction.tolist(), index= df_pred.index)
    df_pred=df_pred.drop(['actual','prediction'], axis = 1)
    df_pred=df_pred.round(1)
    train_pred=list(y_c)
    train_actual=list(y)
    df_train_pred=pd.DataFrame()
    df_train_pred['actual']=train_actual
    df_train_pred['prediction']=train_pred
    df_train_pred[['moisture_actual','fat_actual','protein_actual']] = pd.DataFrame(df_train_pred.actual.tolist(), index= df_train_pred.index)
    df_train_pred[['moisture_predict','fat_predict','protein_predict']] = pd.DataFrame(df_train_pred.prediction.tolist(), index= df_train_pred.index)
    df_train_pred=df_train_pred.drop(['actual','prediction'], axis = 1)
    df_train_pred=df_train_pred.round(1)
    df_train_pred['Wavelength (nm)']=pd.DataFrame(np.arange(0,len(train_pred)))


    y_cv = cross_val_predict(pls_opt, x_final, y, cv=10)
    #y_cv_test = cross_val_predict(pls_opt, actual, pred, cv=1)
    # Calculate scores for calibration and cross-validation
    score_c = r2_score(y, y_c)
    score_cv = r2_score(y, y_cv)
    score_c_test=r2_score(actual, pred)


    # Calculate mean squared error for calibration and cross validation
    mse_c = mean_squared_error(y, y_c)

    mse_cv = mean_squared_error(y, y_cv)
    mse_c_test = mean_squared_error(actual, pred)

    final_mse=mse_df.to_json(orient='records')
    final_pred=df_pred.to_json(orient='records')
    final_loadings=loadings_df.to_json(orient='records')
    final_scores=scores_df.to_json(orient='records')
    final_train=df_train_pred.to_json(orient='records')


    final_data = {'train':final_train,'scores':final_scores,'loadings':final_loadings,
                   'prediction':final_pred,'mse':final_mse,'R2_calib':round(score_c, 2),
                   'R2_cv':round(score_cv, 2),'MSE_calib':round(mse_c, 2),'MSE_cv':round(mse_cv, 2),
                   'R2_calib_pred':round(score_c_test, 2),'MSE_calib_pred':round(mse_c_test, 2)}

    file_path = "Models/"+parent+"/"+child+"/graphs/"
    file_name = file_path+sample_name + "_plsmodel.json"
    json_object = json.dumps(final_data, indent = 4)


    if not os.path.exists(file_path):
         os.makedirs(file_path)
    with open(file_name,'w') as f:
        f.write(json_object)
    return final_data

def upload_predict(df,parent,child,saved_model):
       df1 = df
       #df1 = df1.loc[:, ~df1.columns.str.contains('^Unnamed')]
       df1.dropna(inplace=True)
       samples=df1.index.values.tolist()
       df1=df1.T
       df1.index.names = ['Wavelength']
       df1=df1.reset_index()

       yhat = predict_flow(df,parent,child,saved_model)


       pred=list(yhat)
       df_pred=pd.DataFrame()
       df_pred['samples']=samples

       df_pred['prediction']=pred
       df_pred[['moisture_predict','fat_predict','protein_predict']] = pd.DataFrame(df_pred.prediction.tolist(), index= df_pred.index)
       df_pred=df_pred.round(1)
       df_pred=df_pred.drop('prediction',axis=1)

       final_pred=df_pred.to_json(orient='records')
       return final_pred

from main import *
