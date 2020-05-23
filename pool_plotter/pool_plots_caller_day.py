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
    
# (Copy only files with a specific prefixes, in case there is more than 1 project)
    
upload_folder = '/upload_folder/'
target_folder = '/home/martin/pool_logger_data/'
file_prefix = 'pool_' # May be empty to copy any file
    
    
for file in os.listdir(upload_folder):
    
    if file_prefix and not file.startswith(file_prefix):
        # this file is not our problem
        continue
    
    copyfile(upload_folder + file, target_folder + file)
    
    # Maybe also delete this file?
    
#%% ------ Step 2, call the various sub scripts and have them make their plots ----

import pool_plots_basic_day

water_temp_file, sunambient_temp_file, enclosure_temp_file, cpu_temp_file = pool_plots_basic_day.make_plots()

copyfile(os.path.join(__location__, cpu_temp_file), "/var/www/html/" + cpu_temp_file)
copyfile(os.path.join(__location__, water_temp_file), "/var/www/html/" + water_temp_file)
copyfile(os.path.join(__location__, sunambient_temp_file), "/var/www/html/" + sunambient_temp_file)
copyfile(os.path.join(__location__, enclosure_temp_file), "/var/www/html/" + enclosure_temp_file)


