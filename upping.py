#!/usr/bin/python3

"""
An uptime/top inspired version of ping.
wolfospealain, March 2018.
https://github.com/wolfospealain/upping
"""

import argparse
import sys
import os
import subprocess
import time
from datetime import datetime, timedelta

try:
    from pyaudio import PyAudio, paFloat32
    from numpy import concatenate, arange, sin, float32
    from math import pi


    class Sound:
        """Generate sound. Requires PyAudio & NumPy."""

        def __init__(self, rate=44100, channels=1):
            # Suppress Jack and ALSA error messages on Linux: https://github.com/rtmrtmrtmrtm/weakmon/blob/master/weakaudio.py
            nullfd = os.open("/dev/null", 1)
            oerr = os.dup(2)
            os.dup2(nullfd, 2)
            self.stream = PyAudio().open(format=paFloat32, channels=channels, rate=rate, output=True)
            os.dup2(oerr, 2)
            os.close(oerr)
            os.close(nullfd)
            return

        def play(self, frequency=440, length=1.0, volume=1.0, rate=44100):
            """Play sine wave at frequency, for length, at rate parameters values."""
            self.stream.stop_stream()
            self.stream.start_stream()
            wave = concatenate(
                [sin(arange(length * rate) * frequency * pi * 2 / rate)]) * volume
            self.stream.write(wave.astype(float32).tostring())
            return

except ImportError:
    class Sound():
        def play(self, frequency=None, length=None, volume=None, rate=None):
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

    def light_distance(ms, fraction=2 / 3):
        """Calculate the minimum distance for lightspeed travel (in a cable)."""
        c = 299792458
        km = (c * (ms/1000) * fraction) / 1000 / 2
        return int(km)

    def lightspeed(ms, km):
        """Calculate the fraction of lightspeed."""
        c = 299792458
        percentage = round(km * 2 * 1000 / c / (ms/1000) * 100, 1)
        return percentage

    def text(statistics=False, distance=False, km=0):
        """Generate connection history output."""
        averages = ""
        legend = ""
        if len(Connection.fifteen.times) > len(Connection.five.times):
            legend += "15|"
            averages += str(Connection.fifteen.average()) + "|"
        if len(Connection.five.times) > len(Connection.one.times):
            legend += "5|"
            averages += str(Connection.five.average()) + "|"
        averages += str(Connection.one.average()) + "ms"
        message = Connection.target + ": " + legend + "1m avg. " + averages
        message += " (up " + str(Connection.uptime).split(sep=".")[0] + ") "
        if distance:
            message += "<" + str(Connection.light_distance(Connection.min)) + "km "
        elif km:
            message += "~" + str(Connection.lightspeed(Connection.min, km)) + "%c "
        if statistics:
            message += str(Connection.min) + " <= " + str(Connection.ms) + "ms <= " + str(Connection.max) + " "
        else:
            message += str(Connection.ms) + "ms "
        return message

    def gui_text(statistics, distance, km):
        """Simple connection output for GUI."""
        message = str(Connection.ms) + "ms "
        if distance:
            message += "\n<" + str(Connection.light_distance(Connection.min)) + "km "
        elif km:
            message += "\n~" + str(Connection.lightspeed(Connection.min, km)) + "%c "
        elif statistics:
            message += "\n>=" + str(Connection.min) + "ms\n<=" + str(Connection.max) + "ms"
        else:
            message += "\n" + str(Connection.one.average())
            if len(Connection.five.times) > len(Connection.one.times):
                message += "|" + str(Connection.five.average())
            if len(Connection.fifteen.times) > len(Connection.five.times):
                message += "|" + str(Connection.fifteen.average())
            message += "ms"
        return message

    def error():
        """Generate error message."""
        message = (Connection.error_message + ": down " + str(Connection.uptime).split(sep=".")[0]) + " "
        return message


class Application:

    def __init__(self, statistics, distance, km, filename=None):
        self.statistics = statistics
        self.distance = distance
        self.km = km
        self.filename = filename
        self.last_output = ""

    def update(self, cli=True):
        connected = Connection.up
        if Connection.test():
            output = Connection.text(self.statistics, self.distance, self.km)
            if self.filename and not connected and self.last_output != "":
                File.print(self.last_output)
            if args.audio:
                beep.play(int(1100 - Connection.ms) if Connection.ms < 1000 else 0, .1, args.volume)
            self.last_output = output
            if cli:
                text = output
                if args.record and not connected and self.last_output != "" and not args.quiet:
                        print("@", timestamp())
            else:
                text = Connection.gui_text(self.statistics, self.distance, self.km)
        else:
            text = Connection.error()
            if args.filename and connected and self.last_output != "":
                File.print(self.last_output)
            self.last_output = text
            if args.error:
                beep.play(6000, .05, args.volume)
                beep.play(4000, .05, args.volume)
            if cli and args.record and connected and self.last_output != "" and not args.quiet:
                print("@", timestamp())
        return text


class GUI:

    def __init__(self, screen, app, delay=60000, title="", text_colour = "lightgreen", background_colour = "black", font = "Courier New", font_size = 160):
        self.screen = screen
        self.app = app
        self.delay = delay
        self.screen.title(title)
        self.text_colour = text_colour
        self.background_colour = background_colour
        self.font = font
        self.font_size = font_size
        self.screen.configure(background=self.background_colour)
        self.screen.resizable(width=YES, height=YES)
        self.screen.attributes("-fullscreen", True)
        self.screen.bind("<F11>", self.toggle_fullscreen)
        self.screen.bind("<Escape>", self.end_fullscreen)
        self.text = Text(self.screen, font=(self.font, self.font_size, "bold"), bg=self.background_colour,
                         fg=self.text_colour, border=0, relief=FLAT,
                         highlightbackground="Black")
        self.text.pack(expand=True, fill='both', padx=50, pady=50)
        self.screen.after(0, self.tick, self.delay)

    def toggle_fullscreen(self, event=None):
        self.screen.attributes("-fullscreen", not self.screen.attributes("-fullscreen"))

    def end_fullscreen(self, event=None):
        self.screen.attributes("-fullscreen", False)

    def tick(self, delay):
        text = app.update(False)
        self.text.delete("1.0", END)
        self.text.insert(INSERT, text)
        self.screen.after(delay, self.tick, delay)


def timestamp():
    return datetime.now().strftime('%d/%m/%y %H:%M')


def install(target):
    """Install to target path and set executable permission."""
    if os.path.isdir(target):
        try:
            subprocess.check_output(["cp", "upping.py", target + "/upping"]).decode("utf-8")
            subprocess.check_output(["chmod", "a+x", target + "/upping"]).decode("utf-8")
            print("Installed to " + target + " as upping.\n")
        except:
            print("Not installed.")
            if os.getuid()!=0:
                print("Is sudo required?\n")
            return False
    else:
        print(target, "is not a directory.\n")
        return False


def parse_command_line(version):
    description = "%(prog)s version " + version + ". " \
                  + "An uptime/top inspired version of ping: " \
                  "Displays/records average ping speeds for 15m, 5m, 1m (connection time) < distance km [minimum <= ] current ping ms speed [ <= maximum]. " \
                  "Audible ping speeds and errors. " \
                  "https://github.com/wolfospealain/upping"
    parser = argparse.ArgumentParser(description=description, epilog="CTRL-C to exit.")
    if ".py" in sys.argv[0]:
        parser.add_argument("--install", action="store_true", dest="install", default=False,
                            help="install to Linux destination path (default: " + install_path + ")")
    parser.add_argument("-V", "--version", action="version", version="%(prog)s " + version,
                        help="display version and exit")
    parser.add_argument("-a", "--audio", action="store_true", dest="audio", default=False,
                        help="generate audio tone (for pings under 1000ms) - requires PyAudio & NumPy")
    parser.add_argument("-d", "--distance", action="store_true", dest="distance", default=False,
                        help="estimate distance in km with 2/3 lightspeed")
    parser.add_argument("-e", "--error", action="store_true", dest="error", default=False,
                        help="chirp on connection error - requires PyAudio & NumPy")
    parser.add_argument("-f", "--file", action="store", type=str, dest="filename",
                        help="record connection history to file")
    parser.add_argument("-g", "--graphical", action="store_true", dest="graphical", default=False,
                        help="simple graphical ping display (ESC to leave fullscreen, F11 to toggle)")
    parser.add_argument("-k", "--km", action="store", type=float, dest="km", default=0,
                        help="calculate speed as a fraction of lightspeed")
    parser.add_argument("-p", "--pause", action="store", type=float, dest="seconds", default=2,
                        help="pause seconds between ping requests (default: %(default)s)")
    parser.add_argument("-q", "--quiet", action="store_true", dest="quiet", default=False,
                        help="quiet mode: no display")
    parser.add_argument("-r", "--record", action="store_true", dest="record", default=False,
                        help="display dis/connection history record")
    parser.add_argument("-s", "--statistics", action="store_true",  dest="statistics", default=False,
                        help="display minimum & maximum statistics")
    parser.add_argument("-v", "--volume", action="store", type=float, dest="volume", default=.1,
                        help="audio volume (default: %(default)s)")
    parser.add_argument("destination", type=str, nargs='?', default="8.8.8.8",
                        help="network destination IP or address (default: %(default)s)")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    print("")
    version = "1.0"
    install_path = "/usr/local/bin"
    icon = "/usr/share/icons/gnome/256x256/apps/utilities-terminal.png"
    title = "UpPing"
    args = parse_command_line(version)
    if ".py" in sys.argv[0]:
        if args.install:
            install(install_path if args.destination == "8.8.8.8" else args.destination)
            exit()
    if args.filename:
        File.name = args.filename
    if args.audio or args.error:
        beep = Sound()
    Connection.target = args.destination
    app = Application(args.statistics, args.distance, args.km, args.filename)
    if args.graphical:
        from tkinter import *
        screen = Tk(className=title)
        screen.wm_iconphoto(True, PhotoImage(file=icon))
        gui = GUI(screen, app, args.seconds * 1000, title=title)
        screen.mainloop()
    else:
        try:
            while True:
                Screen.print(app.update())
                time.sleep(args.seconds)
        except KeyboardInterrupt:
            print("\n")
    if args.filename:
        File.print(Connection.text(args.statistics, args.distance, args.km))
