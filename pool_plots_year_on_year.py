# -*- coding: utf-8 -*-
"""
Created on Wed May 19 14:29:58 2021

@author: Martin
"""

# -*- coding: utf-8 -*-
"""
Created on Tue May 18 21:51:35 2021

@author: Martin
"""

# -*- coding: utf-8 -*-
"""
Created on Tue May 12 09:28:59 2020

@author: Martin
"""


import numpy as np
import matplotlib
matplotlib.use('svg')
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from distutils.version import StrictVersion
import datetime
from calendar import monthrange

import dataloader

# Path to current folder for output files
import os
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

# Capture one reference point for "today" 
# (In case the script starts just before midnight, but then
#  rolls over halfway through)
today = datetime.date.today()

#%% Load some data

# Load the current month
now = datetime.datetime.now()
now_year = now.year
month = now.month

nothing_loaded_at_all = True

all_data = []

for years_ago in range(4, -1, -1):
    this_year = now_year-years_ago
    dt_start = datetime.datetime.combine(datetime.date(this_year, 1, 1),  datetime.time(0, 0))
    dt_end = datetime.datetime.combine(datetime.date(this_year, 12, 31),  datetime.time(23, 59))
    
    # It is expected that some data doesn't exist, so do a try catch
    try:
        data_this = dataloader.get_data(dt_start=dt_start, dt_end=dt_end)
        nothing_loaded_at_all = False
        all_data.append(data_this)
    except:
        print(f"Nothing for {this_year}")



@ticker.FuncFormatter
def c2f_formatter(x, pos):
    deg_F = ((x/5)*9)+32
    return f"{deg_F:0.1f}"

#%% Plot function

def make_plot(fnum, all_data, ylab, ylab2, xlim=None):

    
    major_locator = ticker.FixedLocator([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    minor_locator = ticker.MultipleLocator(1)
 
    f,ax1 = plt.subplots(num=fnum, clear=True)

    f.set_size_inches(10, 6)

    present_year = datetime.datetime.now().year
    x_max = 1
    for data in all_data:
        # Calculate difference to current year:
        this_year = data['datetime'][0].astype(object).year
        #this_month = data['datetime'][0].astype(object).month
        month_start_dt64 = np.datetime64(f"{this_year}-01-01", 'ms')
        # Flesh out the year from this
        
        x = (data['datetime'] - month_start_dt64) / np.timedelta64(1, 'D')/365.25*12 + 1.0 
        # Add that amount of years to offset:
      
        
        # Averate the two channels
        y = np.nanmean( np.append(data['pool1'][:, None], data['pool2'][:, None], axis=1), axis=1 )
        
        ax1.plot(x, y, label=f"{this_year}")
        
        x_max = max(x_max, x[-1])
        
    ax1.set_ylabel(ylab)

    l = ax1.legend()

    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    # format the ticks
    ax1.xaxis.set_major_locator(major_locator)
#    ax1.xaxis.set_major_formatter(x_major_fmt)
    ax1.xaxis.set_minor_locator(minor_locator)
#    ax1.xaxis.set_minor_formatter(x_minor_fmt)
    #f.autofmt_xdate()

    ax2 = ax1.twinx()
    ax2.set_ylabel(ylab2)
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=0, horizontalalignment='center' )
    plt.setp(ax1.xaxis.get_minorticklabels(), rotation=0, horizontalalignment='center', fontsize=9 )

    ax1.set_xlabel("Month")
    #ax1.set_title(data['datetime'][0].astype(object).strftime("%b"))
    
    # Adjust x range
    x_min = 1
    x_max = 13
    ax1.set_xlim(x_min, x_max)

    # Round the y axis similarly
    y_min, y_max = ax1.get_ylim()
    yt = ax1.get_yticks()
    ax1.set_ylim(yt[0], yt[-1])
    
    # ax2 is empty, so the default y range is 0.0 to 1.0.
    # Set it to match such that the ticks line up:
    ax2.set_ylim(yt[0], yt[-1])

    # Overwrite the tick decorator to convert C to F dynamically:
    ax2.yaxis.set_major_formatter(c2f_formatter)

    ax1.grid(visible=True, which='major', color=(0.75,0.75,0.75), linestyle='-')
    ax1.grid(visible=True, which='minor', color=(0.8,0.8,0.8), linestyle=':')


    #f.tight_layout()
    return f, ax1

#%%

def make_plots():
  
   
    outfiles = []

    f,a = make_plot('Temperatures',
              all_data,
              "Temperature (°C)", # y/ax1 label
              "(°F)", # y/ax2 label
              #xlim=[xmin,xmax],
              )
    filename = "pool_temp_years_compared.svg"
    f.savefig(os.path.join(__location__, filename))
    outfiles.append(filename)
#
#    f,a = make_plot('sunambient',
#              d['datetime'], # x axis
#              [(d['sunambient'], 'Ambient in sun')], # Y trace(s)
#              "Ambient/sun temperature (°C)", # y/ax1 label
#              "(°F)", # y/ax2 label
#              #xlim=[xmin,xmax],
#              )
#    filename = "sunambient_temp_last_month.svg"
#    f.savefig(os.path.join(__location__, filename))
#    outfiles.append(filename)
#
#
#    f,a = make_plot('Enclosure',
#              d['datetime'], # x axis
#              [(d['enclosure'], 'Enclosure')], # Y trace(s)
#              "Enclosure temperature (°C)", # y/ax1 label
#              "(°F)", # y/ax2 label
#              #xlim=[xmin,xmax],
#              )
#    filename = "enclosure_temp_last_month.svg"
#    f.savefig(os.path.join(__location__, filename))
#    outfiles.append(filename)
#
#    
#    f,a = make_plot('CPU Temperature',
#              d['datetime'], # x axis
#              [(d['cpu_temperature'], 'BMP180')], # Y trace(s)
#              "CPU temperature (°C)", # y/ax1 label
#              "(°F)", # y/ax2 label
#              #xlim=[xmin,xmax],
#              )
#    filename = "pool_cpu_temp_last_month.svg"
#    f.savefig(os.path.join(__location__, filename))
#    outfiles.append(filename)
   
    return outfiles


if __name__ == '__main__':
    make_plots()
