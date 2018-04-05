#!/usr/bin/python3
# wolfospealain, March 2018.
# https://github.com/wolfospealain/upping

import argparse
import sys
import os
import subprocess
import time
from datetime import datetime, timedelta

version = "1.0"
install_path = "/usr/local/bin"

try:
    from pyaudio import PyAudio, paFloat32
    from numpy import concatenate, arange, sin, float32
    from math import pi


    class Sound:
        """Generate sound. Requires PyAudio & NumPy."""

        # Bypass libasound.so error messages.
        def error_output(filename, line, function, err, fmt):
            pass
        from ctypes import CFUNCTYPE, c_char_p, c_int, cdll
        error_handler = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
        c_error_handler = error_handler(error_output)
        cdll.LoadLibrary('libasound.so').snd_lib_error_set_handler(c_error_handler)

        def __init__(self, rate=44100, channels=1):
            self.stream = PyAudio().open(format=paFloat32, channels=channels, rate=rate, output=1)
            return

        def play(self, frequency=440, length=1, rate=44100):
            """Play sine wave at frequency, for length, at rate parameters values."""
            wave = concatenate(
                [sin(arange(int(length * rate)) * float(frequency) * (pi * 2) / rate)]) * .25
            self.stream.write(wave.astype(float32).tostring())
            return

except ImportError:
    class Sound():
        def play(self, frequency=None, length=None, rate=None):
            """No sound available."""
            return


class Screen:
    """Print overwriting output string."""
    printed = 0

    def print(message):
        length = len(message)
        if length < Screen.printed:
            over_write = message + " " * (Screen.printed - length)
            print("\r", over_write, sep="", end="")
        print("\r", message, sep="", end="")
        Screen.printed = length
        return


class File:
    """Output to file."""
    name= ""

    def print(message):
        output = open(File.name, 'a')
        print(timestamp() + ":", message, file=output)
        output.close()
        return


class Log:
    """Record ping speed results for a set period."""
    def __init__(self, minutes=1):
        self.times = []
        self.minutes = minutes
        self.count = 0
        self.total = 0
        return

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
            Connection.min = None
            Connection.max = None
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
        message = Connection.target + ": avg. for "
        if len(Connection.fifteen.times) > len(Connection.five.times):
            message += "15m " + str(Connection.fifteen.average()) + "ms, "
        if len(Connection.five.times) > len(Connection.one.times):
            message += "5m " + str(Connection.five.average()) + "ms, "
        message += "1m " + str(Connection.one.average()) + "ms; now " + str(Connection.ms) + "ms"
        if statistics:
            message += "; min. " + str(Connection.min) + "ms, max. " + str(Connection.max) + "ms"
        if distance:
            message += "; <" + str(Connection.lightspeed(Connection.min)) + "km"
        message += "; up " + str(Connection.uptime).split(sep=".")[0] + " "

        return message

    def error():
        """Generate error message."""
        message = (Connection.error_message + "; down " + str(Connection.uptime).split(sep=".")[0]) + " "
        return message


def timestamp():
    return datetime.now().strftime('%d/%m/%y %H:%M')


def install(target=install_path):
    """Install to target path and set executable permission."""
    if os.path.isdir(target):
        try:
            subprocess.check_output(["cp", "upping.py", target + "/upping"]).decode("utf-8")
            subprocess.check_output(["chmod", "a+x", target + "/upping"]).decode("utf-8")
            print("Installed to " + target + " as upping.")
        except:
            print("Not installed.")
            if os.getuid()!=0:
                print("Is sudo required?")
            return False
    else:
        print(target, "is not a directory.")
        return False


def parse_command_line():
    description = "%(prog)s version " + version + ". " \
                  + "An uptime/top inspired version of ping: " \
                  "Displays/records average ping speeds for 15m, 5m, 1m; current ping speed; [statistics;] " \
                  "[distance (km);] connection time. Audible ping speeds and errors."
    parser = argparse.ArgumentParser(description=description, epilog="CTRL-C to exit.")
    parser.add_argument("--install", action="store_true", dest="install", default=False,
                        help="install to Linux destination path (default: " + install_path + ")")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s " + version,
                        help="display version and exit")
    parser.add_argument("-a", "--audio", action="store_true", dest="audio", default=False,
                        help="generate audio tone (for pings under 1500ms) - requires PyAudio & NumPy")
    parser.add_argument("-d", "--distance", action="store_true", dest="distance", default=False,
                        help="estimate distance in km with 2/3 lightspeed")
    parser.add_argument("-e", "--error", action="store_true", dest="error", default=False,
                        help="chirp on connection error - requires PyAudio & NumPy")
    parser.add_argument("-f", "--file", action="store", type=str, dest="filename",
                        help="record connection history to file")
    parser.add_argument("-p", "--pause", action="store", type=float, dest="seconds", default=2,
                        help="pause seconds between ping requests (default: %(default)s)")
    parser.add_argument("-r", "--record", action="store_true", dest="record", default=False,
                        help="display dis/connection history record")
    parser.add_argument("-s", "--statistics", action="store_true",  dest="statistics", default=False,
                        help="display minimum & maximum statistics")
    parser.add_argument("destination", type=str, nargs='?', default="8.8.8.8",
                        help="network destination IP or address (default: %(default)s)")
    args = parser.parse_args()
    if not args:
        parser.print_help()
        sys.exit(1)
    return args


if __name__ == "__main__":
    args = parse_command_line()
    if args.install:
        install(install_path if args.destination == "8.8.8.8" else args.destination)
        exit()
    if args.filename:
        File.name = args.filename
    if args.audio or args.error:
        beep = Sound()
    Connection.target = args.destination
    first_run = True
    try:
        while True:
            connected = Connection.up
            if Connection.test():
                if args.record and not connected and not first_run:
                    print("@", timestamp())
                    if args.filename:
                        File.print(Connection.output(args.statistics, args.distance))
                Screen.print(Connection.output(args.statistics, args.distance))
                if args.audio:
                    # Range audio between 1100Hz and 100Hz for pings under 1000ms.
                    beep.play(int(1100 - Connection.ms), .5)

            else:
                if args.record and connected and not first_run:
                    print("@", timestamp())
                    if args.filename:
                        File.print(Connection.error())
                Screen.print(Connection.error())
                if args.error:
                    beep.play(6000, .05)
                    beep.play(4000, .05)
            sys.stdout.flush()
            time.sleep(args.seconds)
            first_run = False
    except KeyboardInterrupt:
        print()
        if args.filename:
            File.print(Connection.output(args.statistics, args.percentage))
        sys.exit(0)
