"""GPS NMEA data acquisition and configuration."""


import argparse
import io
import re
import selectors
import time

import pynmea2
import serial
import pymavlink.dialects.v10.ceaufmg as mavlink


def nmea_to_mavlink(msg, time_usec=0):
    if isinstance(msg, pynmea2.types.talker.GGA):
        return mavlink.MAVLink_gps_gga_message(
            time_usec=time_usec, fix_time=total_seconds(msg.timestamp),
            latitude=to_float(msg.latitude), longitude=to_float(msg.longitude),
            quality=msg.gps_qual,  num_sats=msg.num_sats,
            hdop=msg.horizontal_dil, altitude=msg.altitude,
            geoid_height=to_float(msg.geo_sep), age_dgps=to_float(msg.geo_sep),
            dgps_id=msg.ref_station_id
        )
    
    
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
    
    def handle_nmea(self, msg, time_usec):
        pass
    
    def handle_mavlink(self, msg):
        pass
    
    def _parse(self):
        """Parse and reset the message buffer."""
        # Retrieve buffer contents
        text = self.buff.decode(encoding='ascii', errors='ignore')
        time_usec = self.started

        # Reset the buffer
        self.buff.clear()
        self.started = None

        # Parse the NMEA message
        try:
            msg = pynmea2.parse(text)
        except Exception:
            return

        # Handle the NMEA message
        try:
            self.handle_nmea(msg, time_usec)
        except Exception:
            pass
            
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


def total_seconds(t):
    """Total of seconds of a datetime.time instance."""
    if isinstance(t, datetime.time):
        return ((t.hour*60 + t.minute)*60 + t.second + t.microsecond*1e-6)
    else:
        return float('nan')


def to_float(x):
    """Convert argument to float or nan if error."""
    try:
        return float(x)
    except (ValueError, TypeError):
        return float('nan')

def to_int(x):
    """Convert argument to int or -1 if error."""
    try:
        return int(x)
    except (ValueError, TypeError):
        return -1


def program_arguments():
    parser = argparse.ArgumentParser(description='Read GPS stream')
    parser.add_argument('gpsport')
    return parser.parse_args()


if __name__ == '__main__':
    args = program_arguments()

