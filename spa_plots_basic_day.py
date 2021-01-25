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
#from shutil import copyfile
import datetime


import dataloader
import spa_helper

# Store the location of the current file to later print the files
import os
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

#%% Load some data

selected_data = [
     ('datetime',          ('datetime', 'datetime64[ms]'),  0),
     ('CPU temp (°C)',     ('cpu_temperature', 'f4'),       np.NaN),
     ('sun_ambient (°C)',  ('sunambient', 'f4'),            np.NaN),
     ('spa1 (raw)',  ('spa1', 'f4'),            np.NaN),
     ('spa2 (raw)',  ('spa2', 'f4'),            np.NaN),
     ('spa3 (raw)',  ('spa3', 'f4'),            np.NaN),
     ]

d = dataloader.get_data(hours_to_load=27, selected_channels=selected_data) # We want the last 24 hours, +2 more to correlate trends

#%% Inner plot function

@ticker.FuncFormatter
def c2f_formatter(x, pos): # Arguments name x and pos for clarity w.r.t. matplotlib documentation
    deg_F = ((x/5)*9)+32
    return f"{deg_F:0.1f}"

def make_plot(fnum, x, ydata, ylab, ylab2, left_side_formatter=c2f_formatter, finer_ygrid=False):

    hours = mdates.HourLocator(interval=2)   # every year
    minutes = mdates.MinuteLocator(interval=30)  # every half hour
    x_major_fmt = mdates.DateFormatter('%H:%M')


    f, ax1 = plt.subplots(num=fnum, clear=True)

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

    if ylab2 is not None:
        ax2 = ax1.twinx()
        ax2.set_ylabel(ylab2)

        ax2.spines['top'].set_visible(False)
        ax2.spines['left'].set_visible(False)


    # round x range to nearest hours.
    #datemax = np.datetime64(d['datetime'][-1], 'h') + np.timedelta64(1, 'h') # Shows the last 26 hours of data of the data in the dateset. Will freeze when no new data is availalbe.
    datemax = np.datetime64(datetime.datetime.now(), 'h') + np.timedelta64(1, 'h') # Shows the last 26 hours of data, might show empty plot if there is no data    
    datemin = datemax - np.timedelta64(26, 'h') # Exactly one day +2 hours
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
    if ylab2 is not None:
        ax2.set_ylim(yt[0], yt[-1])
    
    # Overwrite the tick decorator to convert C to F dynamically:
    if left_side_formatter is not None:
        ax1.yaxis.set_major_formatter(left_side_formatter)
    
    
    ax1.grid(b=True, which='major', color=(0.75,0.75,0.75), linestyle='-')
    ax1.grid(b=True, which='minor', color=(0.8,0.8,0.8), linestyle=':')

    if finer_ygrid:
        ax1.yaxis.set_minor_locator(ticker.AutoMinorLocator(4))
        ax2.yaxis.set_minor_locator(ticker.AutoMinorLocator(4))
        
        ax1.tick_params(which='minor', 
               length=1.5,
               )
        ax2.tick_params(which='minor', 
               length=1.5,
               )

    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=30, horizontalalignment='right' )

    return f, ax1

def make_plots():
      
    # Convert some
    sensor1_celcius, sensor3_celcius, Arms = spa_helper.convert_raw_values(d)
    
    out_list = [] # Collects filenames
    
    f,a = make_plot('Temperatures',
              d['datetime'], # x axis
              [(sensor1_celcius, 'Sensor 1'), (sensor3_celcius, 'Sensor 3')], # Y trace(s)
              "Temperature (°F)", # y/ax1 label
              "Temperature (°C)", # y/ax2 label
              )
    filename = "spa_temp_last24.svg"
    f.savefig(os.path.join(__location__, filename))
    out_list.append(filename)

    f,a = make_plot('Phase current',
              d['datetime'], # x axis
              [(Arms, 'Current')], # Y trace(s)
              "Phase current (Arms)", # y/ax1 label
              "Phase current (Arms)", # y/ax2 label
              left_side_formatter=None,
              finer_ygrid=True,
              )
    filename = "spa_Iphase_last24.svg"
    f.savefig(os.path.join(__location__, filename))
    out_list.append(filename)


    f,a = make_plot('sunambient',
              d['datetime'], # x axis
              [(d['sunambient'], 'Ambient in sun')], # Y trace(s)
              "Ambient/sun temperature (°F)", # y/ax1 label
              "(°C)", # y/ax2 label
              )
    filename = "spa_sunambient_temp_last24.svg"
    f.savefig(os.path.join(__location__, filename))
    out_list.append(filename)

    f,a = make_plot('Raw values',
              d['datetime'], # x axis
              [(d['spa1'], 'Sensor 1'), (d['spa2'], 'Sensor 2'), (d['spa3'], 'Sensor 3')], # Y trace(s)
              "Raw ADC values (0-1)", # y/ax1 label
              None, # y/ax2 label
              None, # left side formatter
              )
    filename = "spa_raw_values_past24.svg"
    f.savefig(os.path.join(__location__, filename))
    out_list.append(filename)
    
#    f,a = make_plot('CPU Temperature',
#              d['datetime'], # x axis
#              [(d['cpu_temperature'], 'BMP180')], # Y trace(s)
#              "CPU temperature (°F)", # y/ax1 label
#              "(°C)", # y/ax2 label
#              )
#    filename = "spa_cpu_temp_last24.svg"
#    f.savefig(os.path.join(__location__, filename))
#    out_list.append(filename)    

    return out_list

if __name__ == '__main__':
    make_plots()
