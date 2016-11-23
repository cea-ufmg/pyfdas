"""Log MAVLink stream."""


import argparse

from pymavlink import mavutil
import pymavlink.dialects.v10.ceaufmg as mavlink


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", action='store_true',
                        help="print messages to STDOUT")
    parser.add_argument("--device", required=True, help="serial port")
    parser.add_argument("--log", type=argparse.FileType('w'),
                        help="Log file")
    parser.add_argument("--baudrate", type=int, help="serial port baud rate",
                        default=57600)
    args = parser.parse_args()

    conn = mavutil.mavlink_connection(args.device, baud=args.baudrate)
    conn.logfile = args.log

    while True:
        msg = conn.recv_msg()
        if args.verbose and msg is not None:
            print(msg)





if __name__ == '__main__':
    main()
