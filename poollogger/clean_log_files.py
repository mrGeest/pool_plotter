#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 10:57:00 2020

@author: Martin
"""

import os
import sys
import time

#%% Input arguments, if any

if len(sys.argv) - 1:
    days_to_process = int(sys.argv[1])    
else:
    days_to_process = 3
        

#%% config
path = '/data/'

file_extension_list = ['.txt']

#%% Function to re-write a file

def rewrite_file(full_path):
    
    file_name, extension = os.path.splitext(path + item)
    file_name_temp = file_name + '_temp'
    
    print(file_name)
    print(extension)

    header_skipped = False
    with open(full_path, 'r') as fin, open(file_name_temp+extension, 'w') as fout:
        for line in fin:
            
            if not header_skipped:
                fout.write(line)
                header_skipped = True
                continue
            
            line_stripped = line.strip() # remove trailing newline
            
            # throw a warning if any odd character is found
            if any( [c < 32 or c > 127 for c in bytearray(line_stripped, 'ascii')] ):
                # This line has corrupted data. Just toss it
                continue
            else:
                # healthy line, just copy it
                fout.write(line)
                
    # Delete original file
    os.remove(full_path)    
    
    # Rename new file in place of original
    os.rename(file_name_temp+extension, full_path)
    


#%%
d = os.listdir(path)

for item in d:
        
    full_path = path + item
    
    file_name, extension = os.path.splitext(full_path)
    
    if extension not in file_extension_list:
        continue
    
    mtime = os.path.getmtime(full_path)

    age_days = (time.time() - mtime) / 3600 / 24
    if age_days > days_to_process:
        continue
    
    #print(item)
    
    header_skipped = False
    with open(full_path, 'r') as f:
        for line in f:
            
            if not header_skipped:
                header_skipped = True
                continue
            
            line = line.strip() # remove trailing newline
            
            # throw a warning if any odd character is found
            if any( [c < 32 or c > 127 for c in bytearray(line, 'ascii')] ):
                print(f"file {item} has a corrupted line:")
                print(f'"{line}"')
                f.close()
                rewrite_file(full_path)
                break
        
    
