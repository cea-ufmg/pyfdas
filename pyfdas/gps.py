"""GPS NMEA data acquisition and configuration."""


import argparse
import io
import re
import selectors
import time

import pynmea2
import serial
import pymavlink.dialects.v10.ceaufmg as mavlink


class GPSStream:
    
    MAX_BUFF_SIZE = 100
    """Maximum required buffer size."""
    
    def __init__(self, port):
        self.port = serial.Serial(port, timeout=0)
        """GPS serial port stream."""
        
        sel = selectors.DefaultSelector()
        sel.register(port, selectors.EVENT_READ)
        self.sel = sel
        """Stream read selector object."""

        self.started = None
        """Timestamp of receipt of message start marker or `None`."""
        
        self.buff = bytearray()
        """GPS stream receive buffer."""
    
    def handle_nmea(self, msg, time_us):
        pass
    
    def handle_mavlink(self, msg):
        pass
    
    def _parse(self):
        """Parse and reset the message buffer."""
        try:
            text = self.buff.decode('ascii')
            msg = pynmea2.parse(text)
            self.handle_nmea(msg, self.started)
        except Exception:
            #### LOG ERROR
            pass
        finally:
            self.buff.clear()
            self.started = None
    
    def _process(self):
        """Process the GPS stream."""
        # Wait for data to arrive
        selected = self.sel.select()
        if not selected:
            raise InterruptedError

        # Retrieve the data available
        data = self.port.read(self.port.in_waiting)

        # Process each received character
        for char in data:
            if char == ord('$'):
                # Reset buffer and timestamp
                self.started = get_time_us()
                self.buff.clear()
                self.buff.append(char)
            elif self.started:
                self.buff.append(char)
                if char == ord('\n'):
                    self.parse()
                elif len(self.buff) > self.MAX_BUFF_SIZE + 50:
                    del self.buff[:-self.MAX_BUFF_SIZE] # truncate buffer


def get_time_us():
    return int(time.clock_gettime(time.CLOCK_REALTIME) * 1e6)


def program_arguments():
    parser = argparse.ArgumentParser(description='Read GPS stream')
    parser.add_argument('gpsport')
    return parser.parse_args()


if __name__ == '__main__':
    args = program_arguments()

