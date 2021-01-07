#!/usr/bin/env python3

import spidev
import numpy as np

_MAX_SPEED_HZ = 1000000
_MODE = 0b11
_INTERNAL_REF_DISABLE = True
# The low power modes are not used; the PM0/PM1 settings are kept at 0


class ad7888():
        
    def __init__(self, spi_bus=0, spi_device=0):
        self.initialized = False
        self.spi_bus = spi_bus
        self.spi_device = spi_device
        
        # The device doesn't need much initialization. 
        # We'll just do a read and discard the output to
        # ensure that the first channel is set up correctly next time
        self.read_all_channels(oversampling_factor=1)
            
        self.initialized = True
        
            
    def read_all_channels(self, oversampling_factor=4):
        """Reads all channels sequentially.
            Multiple passes are done and averaged (default 4)
            to get more resolution.
            In testing on a raspberry Pi 3B+, each pass takes 0.3 ms
            with a 1 MHz clock. 2 MHz saves time, but slightly skews
            results."""
        
        config_word = 0b00000000
        if _INTERNAL_REF_DISABLE:
            config_word = 0b00000100
            
        outputs = np.zeros(8)
            
        with spidev.SpiDev() as spi:
            spi.open(self.spi_bus, self.spi_device)
            spi.max_speed_hz = _MAX_SPEED_HZ
            spi.mode = _MODE
            for cycle in range(oversampling_factor):
                for addr in range(8):
                    inout_list = [config_word + 8*addr, 0]
                    spi.xfer2(inout_list, _MAX_SPEED_HZ, 0) # The result is both placed in inout_list and returned as return value
                    #print(inout_list, end=' ')
                    #print(inout_list[0]*256 + inout_list[1])
                    
                    outputs[addr] += inout_list[0]*256 + inout_list[1]
                
            
        return outputs/oversampling_factor/4095.0
                    


if __name__ == "__main__":

    import time # We only need time for testing and debug

    print("Starting main")
    
    ad0 = ad7888()
    
    if not ad0.initialized:
        raise Exception("Initialization failed")
     
    print("Init done.")
    
    t0 = time.time()
    values4 = ad0.read_all_channels()
    t1 = time.time()
    values10 = ad0.read_all_channels(oversampling_factor=10)
    t2 = time.time()
    
    print(values4)
    print(values10)
    
    print(f"Time oss=4: {(t1-t0)*1e3:0.2f} ms. {(t1-t0)*1e3/4:0.2f} ms/pass")
    print(f"Time oss=10: {(t2-t1)*1e3:0.2f} ms. {(t2-t1)*1e3/10:0.2f} ms/pass")
    
    while True and False:
        values = ad0.read_all_channels()
        print(' ')
        for index in range(len(values)):
            print('%0.5f' % values[index])
        time.sleep(1)

    print("Main complete")
