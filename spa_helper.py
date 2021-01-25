# -*- coding: utf-8 -*-
"""
Created on Wed Jan  6 20:40:26 2021

@author: Martin
"""

import numpy as np

def convert_raw_values(data):
    
    
    
    def R_to_T_type1(R_ntc):
        # Steinhart-hart (more accurate than just Beta)
        return 1/(0.00112452 + 0.0002350*np.log(R_ntc) + 8.558e-8*np.log(R_ntc)**3)-273

    
    values = data['spa1'] # In the range of 0.0 to 1.0
    R_pullup = 4.7e3
    R_ntc = R_pullup*values/(1-values)
    sensor1_celcius = R_to_T_type1(R_ntc)

    values = data['spa3'] # In the range of 0.0 to 1.0
    R_pullup = 4.7e3
    R_ntc = R_pullup*values/(1-values)
    sensor3_celcius = R_to_T_type1(R_ntc)

    # Do the phase current transducer
    # The sensor converts 0 - 50 Arms to 0-5V
    # This voltage goes through a 8.2 / 15 kOhm divider to step
    # it down to the 3.3 V range that the ADC wants.    
    gain_multiplier_relative_to_Arms = 3.3 * (15+8.2)/15 * 10

    Arms = data['spa2'] * gain_multiplier_relative_to_Arms
    
    

    return sensor1_celcius, sensor3_celcius, Arms