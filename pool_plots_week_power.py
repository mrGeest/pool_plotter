#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  3 11:14:08 2020

@author: Martin
"""


import numpy as np
import matplotlib
matplotlib.use('svg')
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from distutils.version import StrictVersion
import datetime

import dataloader

# Path to current folder for output files
import os
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

# Capture one reference point for "today" 
# (In case the script starts just before midnight, but then
#  rolls over halfway through)
today = datetime.date.today()

#%% Load some data, and setup

water_volume = 128e3 # liters, which is taken to be kg in this script
heat_capacity = 4186 # J/kg/K

pre_filter_cutoff_freq_per_hour = 0.8
post_filter_cutoff_freq_per_hour = 6.2
samples_per_hour = 20

d = dataloader.get_data(hours_to_load=7*24, samples_per_hour=samples_per_hour)


#%% For the 'muricans, show degrees F

@ticker.FuncFormatter
def c2f_formatter(x, pos):
    deg_F = ((x/5)*9)+32
    return f"{deg_F:0.1f}"

#%% Plot function

def make_plot(fnum, x, ydata, ylab, xlim=None, fill_in=True):


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
        if fill_in:
            ax1.fill_between(x, 0, y, label=lab)
        else:
            ax1.plot(x, y, label=lab)
                
    ax1.set_ylabel(ylab)
    if fill_in:
        ax1.set_axisbelow(True) # Needed with the 'fill_between' plots

    if len(ydata) > 1:
        l = ax1.legend()

    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    # format the ticks
    ax1.xaxis.set_major_locator(major_locator)
    ax1.xaxis.set_major_formatter(x_formatter)
    ax1.xaxis.set_minor_locator(minor_locator)
    #f.autofmt_xdate()

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
    

    ax1.grid(b=True, which='major', color=(0.75,0.75,0.75), linestyle='-')
    ax1.grid(b=True, which='minor', color=(0.8,0.8,0.8), linestyle=':')


    #f.tight_layout()
    return f, ax1

#%%

def make_plots(debug=False):

    number_of_days = 7
    start_of_period = datetime.datetime.combine(today-datetime.timedelta(days=number_of_days-1), datetime.datetime.min.time())
    end_of_today = datetime.datetime.combine(today, datetime.datetime.max.time())
    end_of_today = datetime.datetime.combine(today+datetime.timedelta(days=1), datetime.datetime.min.time())


    xmin = np.datetime64(start_of_period)
    xmax = np.datetime64(end_of_today) 
    
    
    b, a = signal.filter_design.butter(2, pre_filter_cutoff_freq_per_hour/samples_per_hour)
    pool1_filtered = signal.filtfilt(b, a, d['pool1'])
    
    temp_rate = np.diff(pool1_filtered)*samples_per_hour/3600 # in degrees per second
    
    heating_power = temp_rate*water_volume*heat_capacity # K/s * kg * J/kg/K = J/s

    b, a = signal.filter_design.butter(2, post_filter_cutoff_freq_per_hour/samples_per_hour)
    heating_power_filtered = signal.filtfilt(b, a, heating_power)

    if debug:
        f,a = make_plot('Temperatures',
                  d['datetime'], # x axis
                  [(d['pool1'], 'Sensor 1'), (pool1_filtered, 'Filtered')], # Y trace(s)
                  "Temperature (°C)", # y/ax1 label
                  xlim=[xmin,xmax],
                  fill_in=False,
                  )
        power_file = "pool_heating_power_filtered_T_last_week.svg"
        f.savefig(os.path.join(__location__, power_file))


    f,a = make_plot('Temperatures',
              d['datetime'][:-1], # x axis
              [ (heating_power_filtered/1e3, 'LPF power')], # Y trace(s)
              "Heating power (kW)", # y/ax1 label
              xlim=[xmin,xmax],
              )
    power_file = "pool_heating_power_last_week.svg"
    f.savefig(os.path.join(__location__, power_file))




    return (power_file, )


if __name__ == '__main__':
    make_plots(debug=True)
