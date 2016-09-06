"""GPS NMEA data acquisition and configuration."""


import argparse
import io
import re
import selectors
import time

import pynmea2
import serial


class GPSStream:
    def __init__(self, port):
        self.port = serial.Serial(port, timeout=0)
        """GPS serial port stream."""
        
        sel = selectors.DefaultSelector()
        sel.register(port, selectors.EVENT_READ)
        self.sel = sel
        """Stream read selector object."""

        self.started = None
        """Timestamp of receipt of message start marker or `None`."""
        
        self.buff = b''
        """GPS stream receive buffer."""

        self.re = re.compile(br'''
            # Message start marker
            \$
        
            # Message type identifier
            (?: (?: G[A-Z]{4}) | (?: P[A-Z]{3}))

            # Message data
            [-.,A-Z0-9]*
        
            # Optional checksum
            (?: \*[0-9A-F]{2})?

            # Message end marker (CR-LF)
            \r\n
            ''', re.X | re.IGNORECASE)
        """NMEA message regular expression."""
    
    def _process(self):
        selected = self.sel.select()
        if not selected:
            raise InterruptedError
        
        timestamp = get_time_us()
        data = self.port.read(self.port.in_waiting)
        self.buff = self.buff + data
        
        out = []
        if self.started and b'\n' in data:
            try:
                out.append(self._parse_one())
            except Exception:
                pass
    
    def _parse_one(self):
        match = self.re.match(self.buff)
        if not match:
            ### clean buffer
            raise ValueError
        
        try:
            msg = pynmea2.parse(match.group())
            msg.time_us = self.started
        finally:
            self.started = None
            self.buff = self.buff[match.end():]
            ### clean buffer up to next $
        
        return msg        


def get_time_us():
    return int(time.clock_gettime(time.CLOCK_REALTIME) * 1e6)


def program_arguments():
    parser = argparse.ArgumentParser(description='Read GPS stream')
    parser.add_argument('gpsport')
    return parser.parse_args()


if __name__ == '__main__':
    args = program_arguments()

