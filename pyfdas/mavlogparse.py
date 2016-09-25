"""MAVLink log parsing utilities."""


import argparse

from pymavlink.dialects.v10 import ceaufmg as mavlink
from pymavlink import mavutil


def main():
    """Parse a MAVLink log."""
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("--condition", default=None,
                        help="message filter condition")
    parser.add_argument("--no-timestamps", dest="notimestamps",
                        action='store_true', help="Log doesn't have timestamps")
    parser.add_argument("--dialect", default="ceaufmg", help="MAVLink dialect")
    parser.add_argument("log", metavar="LOG")
    args = parser.parse_args()
    
    conn = mavutil.mavlink_connection(args.log, dialect=args.dialect,
                                      notimestamps=args.notimestamps)
    while True:
        msg = conn.recv_match(condition=args.condition)
        if msg is None:
            break
        elif msg.get_type() == 'BAD_DATA':
            continue
        else:
            print(msg)

    
if __name__ == '__main__':
    main()
