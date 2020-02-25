# iGate Telemetry

This is a simple program that I use with my APRS iGate using APRS
telemetry to send the status of the node.

## Metrics:

The metrics sent by the iGate are:
 - Load average
 - CPU Temperature
 - Free Memory

## Usage:
```
CBEACON delay=0:45 every=60:00 SENDTO=IG info="Telemetry https://github.com/0x9900/igate_telem"
CBEACON delay=0:10 every=5:00 SENDTO=IG infocmd="/usr/local/bin/aprs_telem --param"
CBEACON delay=0:12 every=5:00 SENDTO=IG infocmd="/usr/local/bin/aprs_telem --unit"
CBEACON delay=0:14 every=5:00 SENDTO=IG infocmd="/usr/local/bin/aprs_telem --eqns"
CBEACON delay=0:15 every=5:00 SENDTO=IG infocmd="/usr/local/bin/aprs_telem --data"
```

## Example:

https://www.aprsdirect.com/details/telemetry/sid/2703346
