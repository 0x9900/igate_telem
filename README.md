# iGate Telemetry

This is a simple program that I use with my APRS iGate using APRS
telemetry to send the status of the node.



## Usage:
```
CBEACON delay=0:10 every=5:00 SENDTO=IG infocmd="/usr/local/bin/telem_temp --param"
CBEACON delay=0:12 every=5:00 SENDTO=IG infocmd="/usr/local/bin/telem_temp --unit"
CBEACON delay=0:14 every=5:00 SENDTO=IG infocmd="/usr/local/bin/telem_temp --eqns"
CBEACON delay=0:15 every=5:00 SENDTO=IG infocmd="/usr/local/bin/telem_temp --data"
```

## Example:

https://www.aprsdirect.com/details/telemetry/sid/2703346
