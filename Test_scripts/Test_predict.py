

import sys
sys.path.insert(1,'../')
from nir_rest import *
from Analysis import *


print(pls('grain','soya_bean','test','SNV',17,2,2,'plsfinal.xlsx'))


predict_pls('Testpls','grain','soya_bean','test_plsmodel','sample1.json')
