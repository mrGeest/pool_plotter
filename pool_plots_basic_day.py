# -*- coding: utf-8 -*-
"""
Created on Tue May 12 09:28:59 2020

@author: Martin
"""


import numpy as np
import matplotlib
matplotlib.use('svg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from distutils.version import StrictVersion
from shutil import copyfile

import dataloader

# Store the location of the current file to later print the files
import os
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

#%% Load some data

d = dataloader.get_data()

#%% Inner plot function

@ticker.FuncFormatter
def c2f_formatter(x, pos):
    deg_F = ((x/5)*9)+32
    return f"{deg_F:0.1f}"

def make_plot(fnum, x, ydata, ylab, ylab2):

    hours = mdates.HourLocator(interval=2)   # every year
    minutes = mdates.MinuteLocator(interval=30)  # every half hour
    x_major_fmt = mdates.DateFormatter('%H:%M')


    f,ax1 = plt.subplots(num=fnum, clear=True)

    f.set_size_inches(10, 6)

    # x comes in as np.datetime64, but older matplotlib versions
    # can't handle this. For those convert to python datetime:
    if StrictVersion(matplotlib.__version__) < StrictVersion('2.2.2'):
        print("Legacy python datetime for the x axis")
        x = x.astype('O')

    for y, lab in ydata:
        ax1.plot(x, y, label=lab)
    ax1.set_ylabel(ylab)

    if len(ydata) > 1:
        l = ax1.legend()

    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    # format the ticks
    ax1.xaxis.set_major_locator(hours)
    ax1.xaxis.set_major_formatter(x_major_fmt)
    ax1.xaxis.set_minor_locator(minutes)

    ax2 = ax1.twinx()
    ax2.set_ylabel(ylab2)

    #f.autofmt_xdate()

    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=30, horizontalalignment='right' )

    # round x range to nearest years.
    datemax = np.datetime64(d['datetime'][-1], 'h') + np.timedelta64(1, 'h')
    #datemin = np.datetime64(d['datetime'][0], 'h') # Auto plot range, will show all data
    datemin = datemax - np.timedelta64(24, 'h') # Exactly one day
    if StrictVersion(matplotlib.__version__) < StrictVersion('2.2.2'):
        datemin = datemin.astype('O')
        datemax = datemax.astype('O')
    ax1.set_xlim(datemin, datemax)

    # Round the y axis similarly
    y_min, y_max = ax1.get_ylim()
    yt = ax1.get_yticks()
    ax1.set_ylim(yt[0], yt[-1])
    
    # ax2 is empty, so the default y range is 0.0 to 1.0.
    # Set it to match such that the ticks line up:
    ax2.set_ylim(yt[0], yt[-1])
    
    # Overwrite the tick decorator to convert C to F dynamically:
    ax2.yaxis.set_major_formatter(c2f_formatter)
    
    
    ax1.grid(b=True, which='major', color=(0.75,0.75,0.75), linestyle='-')
    ax1.grid(b=True, which='minor', color=(0.8,0.8,0.8), linestyle=':')


    #f.tight_layout()
    return f, ax1

def make_plots():
    f,a = make_plot('Temperatures',
              d['datetime'], # x axis
              [(d['pool1'], 'Sensor 1'), (d['pool2'], 'Sensor 2')], # Y trace(s)
              #[(d['temperature1'], 'BMP180')], # Y trace(s)
              "Temperature (°C)", # y/ax1 label
              "(°F)", # y/ax2 label
              )
    water_temp_file = "pool_temp_last24.svg"
    f.savefig(os.path.join(__location__, water_temp_file))

    f,a = make_plot('sunambient',
              d['datetime'], # x axis
              [(d['sunambient'], 'Ambient in sun')], # Y trace(s)
              "Ambient/sun temperature (°C)", # y/ax1 label
              "(°F)", # y/ax2 label
              )
    sunambient_temp_file = "sunambient_temp_last24.svg"
    f.savefig(os.path.join(__location__, sunambient_temp_file))

    f,a = make_plot('Enclosure',
              d['datetime'], # x axis
              [(d['enclosure'], 'Enclosure')], # Y trace(s)
              "Enclosure temperature (°C)", # y/ax1 label
              "(°F)", # y/ax2 label
              )
    enclosure_temp_file = "enclosure_temp_last24.svg"
    f.savefig(os.path.join(__location__, enclosure_temp_file))
    
    f,a = make_plot('CPU Temperature',
              d['datetime'], # x axis
              [(d['cpu_temperature'], 'BMP180')], # Y trace(s)
              "CPU temperature (°C)", # y/ax1 label
              "(°F)", # y/ax2 label
              )
    cpu_temp_file = "pool_cpu_temp_last24.svg"
    f.savefig(os.path.join(__location__, cpu_temp_file))
    

    return water_temp_file, sunambient_temp_file, enclosure_temp_file, cpu_temp_file

if __name__ == '__main__':
    make_plots()
