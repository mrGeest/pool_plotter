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

#Get the current directory, where the image files are also created
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    



#%% ---- Step 1, copy files from the upload folder to the local archiving folder ----
# This only matters on the server, does nothing when running for debugging.

try:
    # path_config will exist on the server
    import path_config    
    upload_folder = path_config.upload_folder
    archive_folder = path_config.data_folder
    web_server_folder = path_config.web_server_folder_pool
except:
    # Probably debug running locally
    upload_folder = None
    archive_folder = '../pool_logger_data/'
    web_server_folder = None
    

file_prefix = 'pool_' # May be empty to copy any file
    
if upload_folder is not None:
    # Do try to copy
    for file in os.listdir(upload_folder):
        
        if file_prefix and not file.startswith(file_prefix):
            # this file is not our problem
            continue
        
        copyfile(upload_folder + file, archive_folder + file)
        
        # Maybe also delete this file?
    
#%% ------ Step 2, call the various sub scripts and have them make their plots ----

def copy_files(files):        
    if web_server_folder is not None:
        for file in files:
            copyfile(os.path.join(__location__, file), web_server_folder + file)

import pool_plots_basic_day
outfiles = pool_plots_basic_day.make_plots()
copy_files(outfiles)
