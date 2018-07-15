# UpPing
An uptime/top inspired version of ping.

## Install (Linux)
```sudo python3 ./upping.py --install```

For audio options:
```pip3 install pyaudio numpy```

## Usage

```
usage: upping [-h] [--install] [-V] [-a] [-d] [-e] [-f FILENAME] [-p SECONDS]
              [-q] [-r] [-s] [-v VOLUME]
              [destination]

upping.py version 1.0. An uptime/top inspired version of ping:
Displays/records average ping speeds for 15m, 5m, 1m (connection time) <
distance km [minimum <= ] current ping ms speed [ <= maximum]. Audible ping
speeds and errors. https://github.com/wolfospealain/upping

positional arguments:
  destination           network destination IP or address (default: 8.8.8.8)

optional arguments:
  -h, --help            show this help message and exit
  --install             install to Linux destination path (default:
                        /usr/local/bin)
  -V, --version         display version and exit
  -a, --audio           generate audio tone (for pings under 1000ms) -
                        requires PyAudio & NumPy
  -d, --distance        estimate distance in km with 2/3 lightspeed
  -e, --error           chirp on connection error - requires PyAudio & NumPy
  -f FILENAME, --file FILENAME
                        record connection history to file
  -p SECONDS, --pause SECONDS
                        pause seconds between ping requests (default: 2)
  -q, --quiet           quiet mode: no display
  -r, --record          display dis/connection history record
  -s, --statistics      display minimum & maximum statistics
  -v VOLUME, --volume VOLUME
                        audio volume (default: 0.1)

CTRL-C to exit.
```

## Use Cases

Simple Internet test: ```upping```

Cable testing: ```upping -e -v .5 -p .5 192.168.0.1```

WiFi/HotSpot connection speed testing: ```upping -a -s -p .5```

Alert on Internet connection error: ```upping -e -v .5 -q```

Monitor Internet connection: ```upping -a -e -p 30```

Monitor server status: ```upping -v .5 -p 60 -e github.com```

Show connection statistics: ```upping -s 172.0.0.1```

Log Internet connection to screen: ```upping -r -s```

Log Internet connection to file: ```upping -q -s -f connection.log```

Estimate maximum distance: ```upping -d github.com```
