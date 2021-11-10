from NIR_Software.application_logging import logger
import os


# below class is used for authentication purposes

class Auth:
    def __init__(self,username,password):
        self.username=username
        self.password=password
        self.file_object = open("Authenticatedusers.txt", 'a+')
        self.log_writer = logger.App_Logger()
    def login(self):
        user=[]
        # create the folder models
        if not os.path.exists("Models"):
            os.makedirs("Models")
        if not os.path.exists("Referrence"):
            os.makedirs("Referrence")
        # Available reference files
        parentFolders= [ name for name in os.listdir('Referrence') if os.path.isdir(os.path.join('Referrence', name)) ]

        #parentFolders=os.listdir('Referrence')
        reference=[]
        child=[]

        for i in parentFolders:
            for j in os.listdir('Referrence/'+i):
                child.append({
                    'childFolder':j,
                    'Files':os.listdir('Referrence/'+i+'/'+j)
                    })

            reference.append({
                'parent':i,
                'child': child

                })
            child=[]

        # login auth
        try:
            if self.username=='admin' and self.password=='admin':
                user={
                    'userName':'Administrator',
                    'email':'admin@elico.co',
                    'role':'Admin',
                    'token':'admin1234',
                     'referrences':reference,
                    'moduleAccess':[{
                        'featureName':'Tasks',
                        'value':1,
                        'type':'screen',

                        'featureAccess':[{
                            'featureName':'Savitzky Golay',
                            'type':'subMenu',
                            'value':1,
                            },
                            {
                            'featureName':'Multi Scatter Correction',
                            'type':'subMenu',
                            'value':1,
                            }]
                        },
                        {
                            'featureName':'Prediction',
                             'value':1
                            },
                         {
                            'featureName':'Model Building',
                        'value':1,
                        'type':'screen',
                        'featureAccess':[{
                            'featureName':'PLS',
                            'type':'subMenu',
                            'value':1,
                            },
                            {
                            'featureName':'PCA',
                            'type':'subMenu',
                            'value':1,
                            }]
                            }]

                    }
                self.log_writer.log(self.file_object,'Admin has logged in')
                return user
            elif self.username=='rajesh' and self.password=='rajesh':
                user={
                    'userName':'Rajesh',
                    'email':'rajesh@elico.co',
                    'role':'Operator',
                    'token':'yasdsakdhsa',
                    'moduleAccess':[{
                        'featureName':'Tasks',
                         'value':0,
                        'type':'screen',
                        'featureAccess':[{
                            'featureName':'Savitzky Golay',
                            'type':'subMenu',
                            'value':0,
                            },
                            {
                            'featureName':'Multi Scatter Correction',
                            'type':'subMenu',
                            'value':0,
                            }]
                        },
                        {
                            'featureName':'Prediction',
                             'value':0
                            },
                         {
                            'featureName':'Model Building',
                        'value':0,
                        'type':'screen',
                        'featureAccess':[{
                            'featureName':'PLS',
                            'type':'subMenu',
                            'value':0,
                            },
                            {
                            'featureName':'PCA',
                            'type':'subMenu',
                            'value':0,
                            }]
                            }]

                    }
                self.log_writer.log(self.file_object,self.username+ 'has logged in')

                return user
        except Exception as e:
                self.log_writer.log(self.file_object,e)
