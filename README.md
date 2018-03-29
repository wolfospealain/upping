# UpPing
An uptime/top inspired version of ping.

```
usage: upping [-h] [--install] [-v] [-d] [-p SECONDS] [-s] [destination]

upping version 1.0. An uptime/top inspired version of ping: Average ping
speeds for 1, 5, 15 min. (statistics); distance (km); connection uptime /
error time; current ping speed.

positional arguments:
  destination           network destination IP or address (default: 8.8.8.8)

optional arguments:
  -h, --help            show this help message and exit
  --install             install to Linux destination path (default:
                        /usr/local/bin)
  -v, --version         display version and exit
  -d, --distance        estimate distance in km with 2/3 lightspeed
  -p SECONDS, --pause SECONDS
                        pause seconds between ping requests (default: 2)
  -s, --statistics      display minimum & maximum statistics

CTRL-C to exit.
```
