"""MAVLink serial port utilities."""


import argparse

from pymavlink.dialects.v10 import ceaufmg as mavlink
from pymavlink import mavutil


mavutil.set_dialect("ceaufmg")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baudrate', type=int, help='serial port baud rate')
    parser.add_argument('--device', required=True, help='serial port')
    parser.add_argument('--logfile', type=argparse.FileType('w'),
                        help='log messages in file')
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()

    conn = mavutil.mavlink_connection(args.device, baud=args.baudrate)
    conn.logfile = args.logfile
    while True:
        msg = conn.recv_msg()
        if msg is not None and args.verbose:
            print(msg)


if __name__ == '__main__':
    main()
