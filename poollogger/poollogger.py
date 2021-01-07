#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

#%% ---------- General setups and imports -------------
import numpy as np
import time
import os

# Sample and logging speed
sample_interval = 2.0    # time between acquisition samples, in seconds
samples_per_log_entry = 8  # Take the average of this number of samples, each captured at sample_interval
# Explanation:
# Samples are captured at `sample_interval`.
# Once `samples_per_log_entry` number of samples have been captured,
# they are averaged and written to the log.
# So:
#  - The interval between log entries is: sample_interval * samples_per_log_entry
#  - Number of samples per hour: 3600/sample_interval/samples_per_log_entry
# Increasing `samples_per_log_entry` and reducing `sample_interval` can
# maintain the same log density, but with increased averaging within every 
# log point, at the cost of system load.

log_file_folder = "/data/"
log_file_prefix = 'pool_' # incase there are mutiple projects in the 

#%% ---------- Interface to the AD7888 ----------------

import AD7888
AD7888_oversampling_factor = 20

ad7888_0 = AD7888.ad7888()

# The interface outputs generic 0-1 numbers. We take
# channels of interest and convert to useful numbers

def process_AD7888_output(values):
    
    assert values.size == 8, "Expected 8 channels"
    
    assert np.all(values <= 1.0) and np.all(values >= 0.0), "Values out of bound"
    
    
    def R_to_T_type1(R_ntc):
        # Steinhart-hart (more accurate than just Beta)
        return 1/(0.00112452 + 0.0002350*np.log(R_ntc) + 8.558e-8*np.log(R_ntc)**3)-273
    
    # Do the box temperature:
    #[0.9998779  0.75931624 0.75594628 0.74202686 0.74217338 0.05909646 0.04368742 0.0]

    ind = 1
    R_pullup = 4.7e3    
    R_ntc = R_pullup*values[ind]/(1-values[ind])
    pool1 = R_to_T_type1(R_ntc)
    
    ind = 2
    R_pullup = 4.7e3    
    R_ntc = R_pullup*values[ind]/(1-values[ind])
    pool2 = R_to_T_type1(R_ntc)
     
    ind = 3
    R_pullup = 4.7e3    
    R_ntc = R_pullup*values[ind]/(1-values[ind])
    control = R_to_T_type1(R_ntc)

    ind = 4
    R_pullup = 4.7e3    
    R_ntc = R_pullup*values[ind]/(1-values[ind])
    enclosure = R_to_T_type1(R_ntc)
    
    ind = 5
    R_pullup = 4.7e3    
    R_ntc = R_pullup*values[ind]/(1-values[ind])
    sunambient = R_to_T_type1(R_ntc)
    
    
    return enclosure, pool1, pool2, sunambient, control
    
#%% ------ Function to write to the logfile ----

def appendToLog(metadata, values):
    """The function automatically creates a new file every hour.
    
    input `metadata` should be an indexable object, with at each index
    another indexable object. These 2-long inner indexable ojects should
    contain: Log file header (string), log number formatter (e.g. '0.2f').
    
    input `values` should have the same length as metadata, and contains
    the values to be printed."""
    
    assert len(metadata) == len(values), 'Inputs must have equal length'
    
    logname = log_file_prefix + time.strftime("%y%m%d%H.txt")
    
    logname = log_file_folder + logname
    
    if not os.path.isfile(logname):
        # Create the file and write the header.
        with open(logname, 'w+') as f:
            header = 'datetime;' + ';'.join([md[0] for md in metadata]) + '\n'
            
            #f.write("datetime;BMP180 temp(C);BMP180 pressure(Pa);si7021 temp(C);si7021 humidity(%%)\n")
            f.write(header)
            
            
    with open(logname, 'a') as f:
        logline = time.strftime("%y%m%d_%H%M%S;") + \
                   ';'.join([f"{v:{md[1]}}" for md, v in zip(metadata, values)]) + \
                   '\n'
        f.write(logline) #time.strftime("%y%m%d_%H%M%S;") + "%0.2f;%0.0f;%0.2f;%0.2f\n" % (T, p, T2, H))

    
    
    
    
#%% ----------------- Main loop --------------


log_metadata = (
      ('CPU temp (°C)', '0.1f'),
      ('enclosure (°C)', '0.2f'),
      ('pool1 (°C)', '0.2f'),
      ('pool2 (°C)', '0.2f'),
      ('sun_ambient (°C)', '0.2f'),
      ('control (°C)', '0.3f'),
      ('spa1 (raw)', '0.4f'),
      ('spa2 (raw)', '0.4f'),
      ('spa3 (raw)', '0.4f'),
      )

n_values = 9
consecutive_failures = 0
max_consecutive_failures = 5
print(log_metadata)
print("Starting while-1 loop")

while True:
    
    
#    try:
        avg_values = np.zeros(n_values)
        for avg_cycle in range(samples_per_log_entry):
            
            # Read the ADC:
            values = ad7888_0.read_all_channels(oversampling_factor=AD7888_oversampling_factor)
            enclosure, pool1, pool2, sunambient, control = process_AD7888_output(values)
            
            # Read the processor temperature
            temp_str = os.popen("vcgencmd measure_temp").readline()
            cpu_temp = float(temp_str.lstrip('temp=').rstrip("'C\n"))
            
            # Combine and add to average:
            avg_values += np.array((cpu_temp, enclosure, pool1, pool2, sunambient, control,
                values[0], values[6], values[7]))
            
            time.sleep(sample_interval)
            
            #print(avg_values)
            
        #haha
            
        print("Logging")
        appendToLog(log_metadata, avg_values/samples_per_log_entry) 
                
        consecutive_failures = 0 # We succeeded, so set failures to 0
        
 #   except:
 #       consecutive_failures += 1 
        
 #       if consecutive_failures > max_consecutive_failures:
 #           print("Failed too often, giving up")
 #           break
        
  #      wait_time = consecutive_failures * 12
  #      print(f"Encountered a fault, waiting for {wait_time} s ...")
  #      time.sleep(wait_time)
  #      print(' ... proceeding.')
        
        
    
    
