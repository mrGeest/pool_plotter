#!/usr/bin/env python3 

from shutil import copyfile

# Run a little after the whole minute
import time
#time.sleep(21)

import dataloader
import numpy as np

# Obtain the temperature
try:
    d = dataloader.get_data(hours_to_load=1)
    temperature = np.nanmean([[-1]['pool1'], d[-1]['pool2']])
except:
    temperature = 0.0

#print(temperature)


# Place the temperature in the header
source_file = '/var/www/html/index2.html'
shadow_file = '/var/www/html/index_temp.html'
out_file = '/var/www/html/index.html'


with open(source_file, 'r') as fin, open(shadow_file, 'w+') as fout:
    for line in fin:
        if '<h1> Water temperature ' in line:
            fout.write(f'<h1> Water temperature {temperature:0.1f}°C</h1>\n')
        else:
            fout.write(line)

# Now swap the files
copyfile(shadow_file, out_file)
