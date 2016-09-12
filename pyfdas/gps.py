"""GPS NMEA data acquisition and configuration."""


import argparse
import datetime
import io
import logging
import os
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
            quality=to_int(msg.gps_qual),  num_sats=to_int(msg.num_sats),
            hdop=to_float(msg.horizontal_dil), altitude=to_float(msg.altitude),
            geoid_height=to_float(msg.geo_sep), age_dgps=to_float(msg.geo_sep),
            dgps_id=msg.ref_station_id
        )
    elif isinstance(msg, pynmea2.types.talker.RMC):
        dt = msg.datetime.replace(tzinfo=datetime.timezone.utc)
        fix_time_usec = dt.timestamp() * 1e6
        return mavlink.MAVLink_gps_rmc_message(
            time_usec=time_usec, fix_time_usec=fix_time_usec,
            warning=msg.status,
            latitude=to_float(msg.latitude), longitude=to_float(msg.longitude),
            speed=msg.spd_over_grnd, course=msg.true_course,
            mag_var=to_float(msg.mag_variation, dir=msg.mag_var_dir),
            mode=''
        )
    
    
class GPSStream:
    
    MAX_BUFF_SIZE = 100
    """Maximum required buffer size."""
    
    def __init__(self, port, logtxtdir=None):
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

        self.logtxt = bool(logtxtdir)
        """Whether to log messages as text."""
        
        self.logtxtdir = logtxtdir
        """Directory to log messages as text."""

        self.text_logs = {}
        """NMEA log files."""

        if self.logtxt:
            os.makedirs(logtxtdir, exist_ok=True)
    
    def handle(self, msg):
        """Handle MAVLink message."""
        # Log as plaintext
        if self.logtxt:
            # Get the log file
            try:
                log = self.text_logs[msg.name]
            except KeyError:
                logname = os.path.join(self.logtxtdir, msg.name + '.log')
                log = file.open(logname, 'wa')
                self.text_logs[msg.name] = log
            # Log the message 
            values = (getattr(msg, f) for f in msg.fieldnames)
            print(*values, file=log)
    
    def _parse_and_handle(self):
        """Parse and reset the message buffer."""
        # Retrieve buffer contents
        text = self.buff.decode(encoding='ascii', errors='ignore')
        time_usec = self.started
        
        # Reset the buffer
        self.buff.clear()
        self.started = None
        
        # Parse the NMEA message
        try:
            nmea_msg = pynmea2.parse(text)
        except ValueError as e:
            logging.error("Error parsing NMEA message, %s", e)

        # Convert to MAVLink
        mavlink_msg = nmea_to_mavlink(nmea_msg)
        if mavlink_msg is None:
            return
        
        # Handle
        try:
            self.handle(mavlink_msg)
        except Exception as e:
            logging.error("Error handling message", exc_info=True)
    
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
    """Total of seconds of datetime.time objects."""
    if isinstance(t, datetime.time):
        return ((t.hour*60 + t.minute)*60 + t.second + t.microsecond*1e-6)
    else:
        return float('nan')


def to_float(x, error=float('nan'), dir='N'):
    """Convert argument to float, treating errors and direction."""
    try:
        sign = -1 if dir in 'SW' else 1
        return float(x) * sign
    except (ValueError, TypeError):
        return error

def to_int(x, error=0):
    """Convert argument to int."""
    try:
        return int(x)
    except (ValueError, TypeError):
        return error


def program_arguments():
    parser = argparse.ArgumentParser(description='Read GPS stream')
    parser.add_argument('gpsport')
    parser.add_argument('--logtxtdir', metavar='DIR',
                        help='write received data as text in DIR')
    return parser.parse_args()


if __name__ == '__main__':
    args = program_arguments()

