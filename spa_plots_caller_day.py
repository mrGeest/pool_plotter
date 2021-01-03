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
    

try:
    # path_config will exist on the server
    import path_config    
    web_server_folder = path_config.web_server_folder_spa
except:
    # Probably debug running locally
    web_server_folder = None
    

#%% ------ Step 2, call the various sub scripts and have them make their plots ----


# lil' helper function
def copy_files(files):        
    if web_server_folder is not None:
        for file in files:
            copyfile(os.path.join(__location__, file), web_server_folder + file)
    

import spa_plots_basic_day

outfiles = spa_plots_basic_day.make_plots()
copy_files(outfiles)
