# -*- coding: utf-8 -*-
"""
Created on Mon May 11 11:53:52 2021

@author: Anisha
"""
#***************************************************
#  Fast API
#***************************************************
import json
from fastapi import FastAPI
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import uvicorn
#***************************************************
#  Fast API
#***************************************************
from pyspectra.transformers.spectral_correction import msc, detrend ,sav_gol,snv

#***************************************************
#  System
#***************************************************

import time
import os
from datetime import datetime
import sys
import logging

from pprint import pformat


from loguru import logger
from loguru._defaults import LOGURU_FORMAT
from starlette.requests import Request
#***************************************************
#  Sensor
#***************************************************

import hid
from Sensor.commands import *
from Sensor.usb_comm import *

from ctypes import *

VID = 0x0451
PID = 0x4200


#***************************************************
#  MISC
#***************************************************

from typing import Any, Dict, AnyStr, List, Union
import pickle
from pickle import dump
import math
import glob


#***************************************************
# Machine Learning
#***************************************************

import pandas as pd
import numpy as np
from scipy import signal
from sklearn.cross_decomposition import PLSRegression
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import mean_squared_error, r2_score


#***************************************************
# GLOBALS
#***************************************************
MAX_PLS_COMPONENTS = 10
