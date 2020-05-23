#!/usr/bin/env python3
"""
Created on Fri Jan  3 22:10:50 2020

@author: Martin
"""
import matplotlib
matplotlib.use('svg')
import numpy as np
import datetime
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from distutils.version import StrictVersion
from shutil import copyfile

# Path to current folder for the image files
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    
#%% ---- Step 1, copy files from the upload folder to the local archiving folder ----

# Actually, don't and rely on the 24 hour plot to have done that for us
   
try:
    # path_config will exist on the server
    import path_config    
    web_server_folder = path_config.web_server_folder
except:
    # Probably debug running locally
    web_server_folder = None
    

#%% ------ Step 2, call the various sub scripts and have them make their plots ----

import pool_plots_basic_week

water_temp_file, sunambient_temp_file, enclosure_temp_file, cpu_temp_file = pool_plots_basic_week.make_plots()

if web_server_folder is not None:
    copyfile(os.path.join(__location__, cpu_temp_file), web_server_folder + cpu_temp_file)
    copyfile(os.path.join(__location__, water_temp_file), web_server_folder + water_temp_file)
    copyfile(os.path.join(__location__, sunambient_temp_file), web_server_folder + sunambient_temp_file)
    copyfile(os.path.join(__location__, enclosure_temp_file), web_server_folder + enclosure_temp_file)


