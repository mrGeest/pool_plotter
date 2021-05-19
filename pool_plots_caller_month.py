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
    web_server_folder = path_config.web_server_folder_pool
except:
    # Probably debug running locally
    web_server_folder = None
    

#%% ------ Step 2, call the various sub scripts and have them make their plots ----

def copy_files(files):        
    if web_server_folder is not None:
        for file in files:
            copyfile(os.path.join(__location__, file), web_server_folder + file)

import pool_plots_basic_month
outfiles = pool_plots_basic_month.make_plots()
copy_files(outfiles)


import pool_plots_month_on_month
outfiles = pool_plots_month_on_month.make_plots()
copy_files(outfiles)
