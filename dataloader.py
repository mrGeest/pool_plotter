# -*- coding: utf-8 -*-
"""
Created on Tue May 12 09:05:09 2020

@author: Martin
"""

import numpy as np
import datetime


file_prefix = 'pool_'

#%% Load PC specific config

try:
    import path_config
    
    data_folder = path_config.data_folder
    
except:
    # Probably debug running locally
    data_folder = 'logdata/'
    

#%% The main externally fonction
    
    
def get_data(hours_to_load=26, 
             samples_per_hour=None, 
             missing_data_threshold_minutes=10):
    """Load data.
    Inputs:
        hours_to_load:
            Specifiy the number of hours to load. Default 26. Must be integer
            
        samples_per_hour:
            Downsample data, useful for longer time range.
            None is default = automatic (starts downsampling above 2 days)
            
        missing_data_threshold_minutes:
            If data is missing for more than this amount of time, insert
            a NaN to break up the plots. 0 disables.
            
    """
        
    now = datetime.datetime.now() # Capture the present time, in case the script runs an hour or day boundary
    
    # Step 1 - Sequentially load all relevant data
    first_file_loaded = False
    
    for hours_ago in range(hours_to_load, -1, -1):
    
        dt = now - datetime.timedelta(hours=hours_ago)
        text_code = data_folder + file_prefix + dt.strftime('%y%m%d%H.txt')
    
        fullfile = text_code
        
        try:
            d_this = _load_file(fullfile)
            #print("Loaded ", fullfile)
        except:
            #print('failded for :', fullfile)
            continue

        if not first_file_loaded:
            # This is the first file that loaded, setup output
            d = d_this
            first_file_loaded = True
        else:
            # append data
            d = np.concatenate((d, d_this))
    
    if not first_file_loaded:
        raise Exception('No data for entire range.')
        
        
    # Step 2 - insert NaNs for gaps in data
    
    if missing_data_threshold_minutes > 0:
        time_s = (d['datetime'] - d['datetime'][0])/ np.timedelta64(1, 's') # Convert date time to seconds
        t_delta = np.diff(time_s)
        gaps = np.where(t_delta > missing_data_threshold_minutes*60)[0]
        
        # Insert a NaN after each occurence
        points_inserted = 0
        for index in range(len(gaps)):
            # Creata a fake date time
            gi = gaps[index] + points_inserted
            gap_time = (d['datetime'][gi+1] - d['datetime'][gi]) 
            dt_fake = d['datetime'][gi] + np.timedelta64(gap_time/2, 's')
            
            # Create a fake line
            line = np.copy(d[gi])
            for name in d[gi].dtype.names:
                if name == 'datetime':
                    line[name] = dt_fake
                else:
                    line[name] = np.NaN
            
            points_inserted += 1
            
    # Step 3 - downsample data
    if samples_per_hour is None:
        # Automatic mode
        if hours_to_load <= 48:
            # 2 days, no downsampling
            samples_per_hour = 0
        elif hours_to_load  <= 7*24:
            # At most 1 week
            samples_per_hour = 30
        else:
            # Loooong
            samples_per_hour = 5000/hours_to_load
            
    if samples_per_hour > 0:
        # Greater than 0 means downsampling must be applied.
        # samples_per_hour might be fractional
        
        expected_max_num_data_points = int(samples_per_hour * hours_to_load)
    
        bin_width_minutes = 10 # 7*24*6 = 1008 datapoints in a week with 10 minute bins

        d_ds = np.zeros(expected_max_num_data_points, dtype=d.dtype)
                
        starting_time = d['datetime'][0]
        starting_index = 0
        vector_index = 0
        while starting_time < d['datetime'][-1]:
            end_time = starting_time + np.timedelta64(bin_width_minutes, 'm')
            
            #To save CPU time on the poor *pi, we'll keep track of indexes
            # (instead of re-determinng the index every time again)
            ending_index = starting_index + 1
            while ending_index < len(d) and d['datetime'][ending_index] < end_time:
                ending_index += 1
                
            # Average over the given window
            for name in d.dtype.names:
                if name == 'datetime':
                    d_ds[name][vector_index] = starting_time + (end_time-starting_time)/2
                else:
                    d_ds[name][vector_index] = np.mean(d[name][starting_index:ending_index])
                       
            # We done?
            if ending_index >= len(d):
                break
            
            # Set up for next loop
            vector_index += 1
            starting_index = ending_index
            starting_time = d['datetime'][starting_index]

        return d_ds[:vector_index]
        
    return d


#%%


def _load_file(filename):
    dtype = [('datetime', 'datetime64[ms]'),
             ('cpu_temperature', 'f4'),
             ('enclosure', 'f4'),
             ('pool1', 'f4'),
             ('pool2', 'f4'),
             ('sunambient', 'f4'),
             ]


    def parsetime(v):
        return np.datetime64(
            datetime.datetime.strptime(v.decode('ascii'), '%y%m%d_%H%M%S')
        )

    data = np.loadtxt(filename, dtype=dtype,
               delimiter=';',
               skiprows=1,
               converters={0: parsetime},
               )


    return data


