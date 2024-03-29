# iGate Telemetry

This is a simple program that I use with my APRS iGate using APRS
telemetry to send the status of the node.

## Metrics:

The metrics sent by the iGate are:
 - Load average
 - CPU Temperature
 - Free Memory
 - Network Tx packets
 - Network Rx packets

## Installation

Before installing igate_telem edit the file igate/telem.py and set the
variable `CALL_SIGN` with your own call sign, then remove the
following line.

Once your call sign has been set run the following command to install the program.

```
sudo python setup.py install
```


## Usage:

```
pi@igate:~ $ igate_telem --help
usage: igate_telem [-h] [-c CALLSIGN] (-d | -e | -p | -u)

APRS RaspberryPi temperature

optional arguments:
  -h, --help            show this help message and exit
  -c CALLSIGN, --callsign CALLSIGN
                        iGate full callsign [default: W6BSD-5
  -d, --data            Send the APRS data
  -e, --eqns            Send the APRS equation
  -p, --param           Send the APRS param
  -u, --unit            Send the APRS units
```

## Direwolf Configuration

```
CBEACON delay=0:45 every=60:00 SENDTO=IG info="> Telemetry https://github.com/0x9900/igate_telem"
CBEACON delay=0:10 every=5:00 SENDTO=IG infocmd="/usr/local/bin/igate_telem --param"
CBEACON delay=0:12 every=5:00 SENDTO=IG infocmd="/usr/local/bin/igate_telem --unit"
CBEACON delay=0:14 every=5:00 SENDTO=IG infocmd="/usr/local/bin/igate_telem --eqns"
CBEACON delay=0:15 every=5:00 SENDTO=IG infocmd="/usr/local/bin/igate_telem --data"
```

## Example:

https://aprs.fi/telemetry/a/W6BSD-5

## Blog post

You can find more information on how to use and configure this program on my [blog post][1]

[1]: https://0x9900.com/aprs-telemetry/
