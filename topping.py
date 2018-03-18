#!/usr/bin/python3
# wolfospealain, March 2018.

import argparse
import sys
import subprocess
import time
from datetime import datetime, timedelta

VERSION = "1.0"

class Screen:
    """Print overwriting output string."""
    printed = 0

    def print(message):
        length = len(message)
        if length < Screen.printed:
            message += " " * (Screen.printed - length)
        Screen.printed = length
        print("\r", message, sep="", end="")
        return


class Log:
    """Record ping speed results for a set period."""
    def __init__(self, minutes=1):
        self.times = []
        self.minutes = minutes
        self.count = 0
        self.total = 0

    def add(self, ping):
        """Add new ping test result to the period log. Remove older entries."""
        self.count += 1
        self.total += ping
        now=datetime.now()
        self.times += [[now, ping]]
        for entry in self.times:
            if (now-entry[0])>timedelta(0,(self.minutes*60)-1,0):
                self.total -= entry[1]
                self.count -= 1
                self.times.remove(entry)
            else:
                break
        return

    def average(self):
        """Return the average ping speed for the period."""
        if self.count > 0:
            return int(self.total/self.count)


class Ping:
    """System ping command."""
    _argument = "-c 1" if sys.platform.find("Linux") else "-t 1"

    def send(target="8.8.8.8"):
        """Send ping test to target."""
        try:
            output = subprocess.check_output(["ping", Ping._argument, target], stderr=subprocess.DEVNULL).decode("utf-8")
            ms = eval(output[output.find("time=") + 5:output.find(" ms")])
            return ms
        except KeyboardInterrupt:
            print()
            sys.exit(0)
        except:
            return False

class Connection:
    """Connection status and history."""
    _clock = datetime.now()
    target = "8.8.8.8"
    ms = None
    up = False
    min = None
    max = None
    uptime = timedelta(seconds=0)
    error_message = "Connection error"
    one = Log(minutes=1)
    five = Log(minutes=5)
    fifteen = Log(minutes=15)

    def test():
        """Ping test."""
        now = datetime.now()
        Connection.ms = Ping.send(Connection.target)
        if Connection.ms:
            # Update logs.
            Connection.one.add(Connection.ms)
            Connection.five.add(Connection.ms)
            Connection.fifteen.add(Connection.ms)
            # Update statistics.
            if Connection.min:
                if Connection.ms < Connection.min:
                    Connection.min = Connection.ms
            else:
                Connection.min = Connection.ms
            if Connection.max:
                if Connection.ms > Connection.max:
                    Connection.max = Connection.ms
            else:
                Connection.max = Connection.ms
            # Update uptime.
            if Connection.up:
                Connection.uptime = now - Connection._clock
            else:
                Connection._clock = now
                Connection.uptime = timedelta(seconds=0)
                Connection.up = True
            return Connection.ms
        else:
            # Reset logs on error.
            Connection.one = Log(minutes=1)
            Connection.five = Log(minutes=5)
            Connection.fifteen = Log(minutes=15)
            # Update uptime.
            if Connection.up:
                Connection._clock = now
                Connection.uptime = timedelta(seconds=0)
                Connection.up = False
            else:
                Connection.uptime = now - Connection._clock
            return False

    def lightspeed(ms, percentage=2/3):
        """Calculate the minimum distance for lightspeed travel (in a cable)."""
        c = 299792458
        km = (c * (ms/1000) * percentage) / 1000 / 2
        return int(km)

    def output(statistics=False, distance=False):
        """Generate connection history output."""
        message = Connection.target + ": " + str(Connection.one.average()) + "ms"
        if len(Connection.five.times) > len(Connection.one.times):
            message += ", " + str(Connection.five.average()) + "ms"
            if len(Connection.fifteen.times) > len(Connection.five.times):
                message += ", " + str(Connection.fifteen.average()) + "ms"
        if statistics:
            message += " (min. " + str(Connection.min) + "ms, max. " + str(Connection.max) + "ms)"
        if distance:
            message += "; <" + str(Connection.lightspeed(Connection.min)) +"km"
        message += "; " + str(Connection.uptime) + ". " + str(Connection.ms) + "ms "

        return message

    def error():
        """Generate error message."""
        message = (Connection.error_message + "; " + str(Connection.uptime))
        return message


def parse_command_line():
    description = "%(prog)s version " + VERSION + ". " \
                  + "A top/uptime inspired version of ping: " \
                  "Average ping speeds for 1, 5, 15 min. (statistics); " \
                  "distance (km); connection uptime / error time. " \
                  "Current ping speed."
    parser = argparse.ArgumentParser(description=description, epilog="CTRL-C to exit.")
    parser.add_argument("-v", "--version", help="display version and exit",
                        action="version", version="%(prog)s " + VERSION)
    parser.add_argument("-d", "--distance", help="estimate distance in km with 2/3 lightspeed",
                      action="store_true", dest="percentage", default=False, )
    parser.add_argument("-p", "--pause", help="pause seconds between ping requests (default: %(default)s)",
                      action="store", dest="seconds", default=1, )
    parser.add_argument("-s", "--statistics", help="display minimum & maximum statistics",
                      action="store_true",  dest="statistics", default=False, )
    parser.add_argument("destination", type=str, nargs=1, help="network destination IP or address")
    args = parser.parse_args()
    if not args:
        parser.print_help()
        sys.exit(1)
    return args


if __name__ == "__main__":
    args = parse_command_line()
    Connection.target = args.destination[0]
    try:
        while True:
            if Connection.test():
                Screen.print(Connection.output(args.statistics, args.percentage))
            else:
                Screen.print(Connection.error())
            sys.stdout.flush()
            time.sleep(args.seconds)
    except KeyboardInterrupt:
        print()
        sys.exit(0)
