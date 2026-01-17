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
    data_folder = '../pool_logger_data/'
    

#%% The main externally fonction
    
    
def get_data(hours_to_load=26, 
             samples_per_hour=None, 
             missing_data_threshold_minutes=10,
             selected_channels=None,
             dt_start=None,
             dt_end=None):
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
            
        dt_start:
            Alternative to hours_to_load. If dt_start is not None, data is loaded from this date time object onwards
            dt_end must not be empty
        
        dt_end:
            loads data up to this datetime. Ignored if dt_start=None
            
            
    """
        
    now = datetime.datetime.now() # Capture the present time, in case the script runs an hour or day boundary
    
    # Step 1 - Sequentially load all relevant data
    # Step 1a, compile a list of files that need to be loaded
    files_to_load = []
    
    if dt_start is None:
        # Simple mode, where we load from x hours ago, till the present
        for hours_ago in range(hours_to_load, -1, -1):
        
            dt = now - datetime.timedelta(hours=hours_ago)
            text_code = data_folder + file_prefix + dt.strftime('%y%m%d%H.txt')
        
            files_to_load.append(text_code)

    else:
        # More advanced mode, where a specific range is loaded.
        dt_running = dt_start
        step = datetime.timedelta(hours=1)
        while dt_running < dt_end:
            
            full_file = data_folder + file_prefix + dt_running.strftime('%y%m%d%H.txt')
            
            files_to_load.append(full_file)
            
            dt_running += step
            
        # Calculate hours to load, as it is still used for tge dow sample filter
        hours_to_load = (dt_end - dt_start)/datetime.timedelta(hours=1)
        
    #print(files_to_load)
    
    # Step 1b, load that list of files
    first_file_loaded = False
    
    for fullfile in files_to_load:
        
        try:
            d_this = _load_file(fullfile, selected_channels=selected_channels)
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
        d = insert_NaNs_for_gaps(d, missing_data_threshold_minutes) 
            
            
    # Step 3 - downsample data
    if samples_per_hour is None:
        # Automatic mode
        if hours_to_load <= 48:
            # 2 days, no downsampling
            samples_per_hour = 0
        elif hours_to_load  <= 7*24:
            # At most 1 week
            samples_per_hour = 6
        else:
            # Loooong
            samples_per_hour = 2000/hours_to_load
            
            
            
    if samples_per_hour > 0:
        # Greater than 0 means downsampling must be applied.
        # samples_per_hour might be fractional
        
        expected_max_num_data_points = int(samples_per_hour * hours_to_load)
    
        bin_width_seconds = int(3600.0/samples_per_hour) # Must be integer, np.timedelta64 is a bit stupid

        d_ds = np.zeros(expected_max_num_data_points, dtype=d.dtype)
                
        starting_time = d['datetime'][0]
        starting_index = 0
        vector_index = 0
        while starting_time < d['datetime'][-1]:
            end_time = starting_time + np.timedelta64(bin_width_seconds, 's')
            
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
                    d_ds[name][vector_index] = np.nanmean(d[name][starting_index:ending_index])
                       
            # We done?
            if ending_index >= len(d):
                break
            
            # Set up for next loop
            vector_index += 1
            starting_index = ending_index
            starting_time = d['datetime'][starting_index]

        # The nanmean might have stripped any gap, so re-insert the gap
        #d_ds = insert_NaNs_for_gaps(d_ds[:vector_index], missing_data_threshold_minutes)???

        return d_ds[:vector_index]
        
    return d


#%%


def _load_file(filename, selected_channels=None):
    
    # Data description should look like a list :
    # ('log file header name (exact)', ('fieldname_for_numpy', 'dtype'), fill_value)
    # Extra header columns are ignored
    # Missing columns are filled out with NaN
    if selected_channels is None:
        data_description = [
             ('datetime',          ('datetime', 'datetime64[ms]'),  0),
             ('CPU temp (°C)',     ('cpu_temperature', 'f4'),       np.nan),
             ('enclosure (°C)',    ('enclosure', 'f4'),             np.nan),
             ('pool1 (°C)',        ('pool1', 'f4'),                 np.nan),
             ('pool2 (°C)',        ('pool2', 'f4'),                 np.nan),
             ('control (°C)',      ('control', 'f4'),               np.nan),
             ('sun_ambient (°C)',  ('sunambient', 'f4'),            np.nan),
             ]
    else:
        data_description = selected_channels
    
    desired_fields = [ t[0] for t in data_description ]

    # For each header name, find the column in the file with the exact same
    # name, and if it exists, note down the column index
    
    # First get the header from the file
    with open(filename, 'r', encoding="utf-8") as f:
        header = f.readline().strip()
        file_fields = header.split(';')
                
    # For each field in the file header, see if we need to load it, and if so,
    # find the column it should end up under
    file_col_indices = [file_fields.index(desired_field) for desired_field in desired_fields if desired_field in file_fields]
    
    # Prepare dtype:
    dtype = [dtype for desired_field, dtype, *_ in data_description if desired_field in file_fields]
    
    # At this point, we have done what we need to:
    # - handle extra columns we don't need
    # - handle arbitrarily arranged columns (except for the datetime, because of the converter function)
        
    def parsetime(v):
        return np.datetime64(
            datetime.datetime.strptime(v.decode('ascii'), '%y%m%d_%H%M%S')
        )
    
    data = np.loadtxt(filename, dtype=dtype,
               delimiter=';',
               skiprows=1,
               usecols=tuple(file_col_indices),
               converters={0: parsetime},
               )
    
    # We still need to handle columns not in the file
    not_in_file = [field not in file_fields for field, *_ in data_description]
        
    if any(not_in_file):
        
        # Create an empty sturctured array, and copy over columns
        # (the copy action seems unavoidable anyway, so might as well  do something
        # conceptually simple.)
        
        n_rows = data.shape[0]        
        dtype = [dtype for _, dtype, *_ in data_description]        
        data_out = np.zeros(n_rows, dtype=dtype)
        
        # Copy existing:
        for dfield in data.dtype.names:
            data_out[dfield] = data[dfield]
            
        # Substitute missing values
        for desired_field, dtype, fill_value, *_ in data_description:
            if desired_field in file_fields:
                continue
            
            data_out[dtype[0]] = fill_value
            
        data = data_out         
    
    # Do some quick and dirty fixes on the data fields:
    if 'pool1' in data.dtype.names:
        broken_sensor = data['pool1'] < -5.0
        data['pool1'][broken_sensor] = np.nan

    if 'pool2' in data.dtype.names:
        broken_sensor = data['pool2'] < -5.0
        data['pool2'][broken_sensor] = np.nan

    if 'sunambient' in data.dtype.names:
        broken_sensor = data['sunambient'] < -10.0
        data['sunambient'][broken_sensor] = np.nan

    return data


#%%
    
def insert_NaNs_for_gaps(d, missing_data_threshold_minutes):
    
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
                line[name] = np.nan
                
        # Insert the line
        d = np.insert(d, gi, line)
        
        points_inserted += 1

    return d


#%% Testing code
    
if __name__ == "__main__":
    
    data = get_data(17)
    print(data)
    
