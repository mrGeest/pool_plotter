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

import dataloader
import spa_helper

# Path to current folder for output files
import os
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

# Capture one reference point for "today" 
# (In case the script starts just before midnight, but then
#  rolls over halfway through)
today = datetime.date.today()

#%% Load some data

selected_data = [
     ('datetime',          ('datetime', 'datetime64[ms]'),  0),
     ('CPU temp (°C)',     ('cpu_temperature', 'f4'),       np.NaN),
     ('sun_ambient (°C)',  ('sunambient', 'f4'),            np.NaN),
     ('spa1 (raw)',  ('spa1', 'f4'),            np.NaN),
     ('spa2 (raw)',  ('spa2', 'f4'),            np.NaN),
     ('spa3 (raw)',  ('spa3', 'f4'),            np.NaN),
     ]

d = dataloader.get_data(hours_to_load=7*24, selected_channels=selected_data)

# Helper function

@ticker.FuncFormatter
def c2f_formatter(x, pos):
    deg_F = ((x/5)*9)+32
    return f"{deg_F:0.1f}"

#%% Plot function

def make_plot(fnum, x, ydata, ylab, ylab2, xlim=None, left_side_formatter=c2f_formatter, finer_ygrid=False):


    major_locator = mdates.HourLocator(interval=12)   # every year
    minor_locator = mdates.HourLocator(interval=2)  # every half hour
    x_major_fmt = mdates.DateFormatter('%H:%M')
    
    # Use a custom formatter function to mark noon special
    @ticker.FuncFormatter
    def x_formatter(x, pos):
        # Get the "stock" xtick label:
        xlab_default = x_major_fmt(x, pos)

        if xlab_default != "00:00":
            # No label
            return " "

        # Must be midnight!
        return mdates.DateFormatter('%A')(x)
        # Figure out which day

        return "noon"

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
    ax1.xaxis.set_major_locator(major_locator)
    ax1.xaxis.set_major_formatter(x_formatter)
    ax1.xaxis.set_minor_locator(minor_locator)
    #f.autofmt_xdate()

    ax2 = ax1.twinx()
    ax2.set_ylabel(ylab2)
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=30, horizontalalignment='right' )

    
    # Adjust x range
    if xlim is None:
        # round x range to nearest hours
        datemin = np.datetime64(d['datetime'][0], 'h')
        datemax = np.datetime64(d['datetime'][-1], 'h') + np.timedelta64(1, 'h')
    else:
        datemin = xlim[0]
        datemax = xlim[1]
        
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


    #f.tight_layout()
    return f, ax1

#%%

def make_plots():
    
    # Convert some
    sensor1_celcius, sensor3_celcius, Arms = spa_helper.convert_raw_values(d)
    
    number_of_days = 7
    start_of_period = datetime.datetime.combine(today-datetime.timedelta(days=number_of_days-1), datetime.datetime.min.time())
    end_of_today = datetime.datetime.combine(today, datetime.datetime.max.time())
    end_of_today = datetime.datetime.combine(today+datetime.timedelta(days=1), datetime.datetime.min.time())


    xmin = np.datetime64(start_of_period)
    xmax = np.datetime64(end_of_today) #+ np.timedelta64(1, 'ms')
    
    out_list = []

    f,a = make_plot('Phase current',
              d['datetime'], # x axis
              [(Arms, 'Current')], # Y trace(s)
              "Phase current (Arms)", # y/ax1 label
              "Phase current (Arms)", # y/ax2 label
              left_side_formatter=None,
              finer_ygrid=True,
              )
    filename = "spa_Iphase_past_week.svg"
    f.savefig(os.path.join(__location__, filename))
    out_list.append(filename)

    f,a = make_plot('Temperatures',
              d['datetime'], # x axis
              [(sensor1_celcius, 'Sensor 1'), (sensor3_celcius, 'Sensor 2')], # Y trace(s)
              "Temperature (°C)", # y/ax1 label
              "(°F)", # y/ax2 label
              xlim=[xmin,xmax],
              )
    filename = "spa_temp_past_week.svg"
    f.savefig(os.path.join(__location__, filename))
    out_list.append(filename)

    f,a = make_plot('sunambient',
              d['datetime'], # x axis
              [(d['sunambient'], 'Ambient in sun')], # Y trace(s)
              "Ambient/sun temperature (°C)", # y/ax1 label
              "(°F)", # y/ax2 label
              xlim=[xmin,xmax],
              )
    filename = "spa_sunambient_temp_last_week.svg"
    f.savefig(os.path.join(__location__, filename))
    out_list.append(filename)


#    f,a = make_plot('Enclosure',
#              d['datetime'], # x axis
#              [(d['enclosure'], 'Enclosure')], # Y trace(s)
#              "Enclosure temperature (°C)", # y/ax1 label
#              "(°F)", # y/ax2 label
#              xlim=[xmin,xmax],
#              )
#    filename = "spa_enclosure_temp_last_week.svg"
#    f.savefig(os.path.join(__location__, filename))
#    out_list.append(filename)

    
#    f,a = make_plot('CPU Temperature',
#              d['datetime'], # x axis
#              [(d['cpu_temperature'], 'BMP180')], # Y trace(s)
#              "CPU temperature (°C)", # y/ax1 label
#              "(°F)", # y/ax2 label
#              xlim=[xmin,xmax],
#              )
#    filename = "spa_pool_cpu_temp_last_week.svg"
#    f.savefig(os.path.join(__location__, filename))
#    out_list.append(filename)
   
    
#    f,a = make_plot('Control Temperature',
#              d['datetime'], # x axis
#              [(d['control'], 'Control')], # Y trace(s)
#              "Reference temperature (°C)", # y/ax1 label
#              "(°F)", # y/ax2 label
#              xlim=[xmin,xmax],
#              )
#    filename = "spa_pool_control_temp_past_week.svg"
#    f.savefig(os.path.join(__location__, filename))
#    out_list.append(filename)
    
    
    return out_list


if __name__ == '__main__':
    make_plots()
