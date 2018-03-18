# TopPing
A top/uptime inspired version of ping.

```
usage: topping.py [-h] [-v] [-d] [-p SECONDS] [-s] destination

topping.py version 1.0. A top/uptime inspired version of ping: Average ping
speeds for 1, 5, 15 min. (statistics); distance (km); connection uptime /
error time. Current ping speed.

positional arguments:
  destination           network destination IP or address

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         display version and exit
  -d, --distance        estimate distance in km with 2/3 lightspeed
  -p SECONDS, --pause SECONDS
                        pause seconds between ping requests (default: 2)
  -s, --statistics      display minimum & maximum statistics

CTRL-C to exit.
```
