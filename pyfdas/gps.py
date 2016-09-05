'''GPS NMEA data acquisition and configuration.'''


import argparse
import io
import selectors
import time

import pynmea2
import serial


class GPSStream:
    def __init__(self, port):
        self.port = serial.Serial(port, timeout=0)
        '''GPS serial port stream.'''
        
        sel = selectors.DefaultSelector()
        sel.register(port, selectors.EVENT_READ)
        self.sel = sel
        '''Stream read selector object.'''

        self.started = None
        '''Timestamp of receipt of message start marker or `None`.'''

        self.buff = io.BytesIO()
        

    def _process(self):
        selected = self.sel.select()
        if not selected:
            return

        data = self.port.read(100)
        if b'$' in data:
            self.started = get_time_us()

        ### remove all content up to $
        
        self.buff.write(data)
        if b'\r\n' in data:
            pass
        

    
    def get_message(self):
        while True:
            selected = self.sel.select()
        for key, events in selected:
            pass
        
        self.port.read()
        

def get_time_us():
    return int(time.clock_gettime(time.CLOCK_REALTIME) * 1e6)


def program_arguments():
    parser = argparse.ArgumentParser(description='Read GPS stream')
    parser.add_argument('gpsport')
    return parser.parse_args()


if __name__ == '__main__':
    args = program_arguments()

