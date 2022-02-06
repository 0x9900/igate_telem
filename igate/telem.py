#!/usr/bin/env python
#
# (c) 2020 Fred C. (W6BSD)
# https://github.com/0x9900/igate_telem
#
# EQNS. is a, b, c | DisplayValue = a * val ^ 2 + b * val + c
# pylint: disable=missing-docstring

__author__ = "Fred C."
__email__ = "<github-fred@hidzz.com>"
__version__ = '0.1.2'

import pickle
import itertools
import os
import re
import time

from argparse import ArgumentParser
from collections import Mapping
from functools import partial

# Insert at the end of the following line your callsign and SSID. Dont
# forget the quotes. Example: CALL_SIGN = "W6BSD-5"
CALL_SIGN = "W6BSD-5"
raise SystemError("Configure your callsign and remove this line")

TMPDIR = os.getenv('XDG_RUNTIME_DIR', '/tmp')
STATUS_FILE = os.path.join(TMPDIR, "aprs_status.dat")

LOADAVG_FILE = "/proc/loadavg"
MEMINFO_FILE = "/proc/meminfo"

THERMFILE = "/sys/class/thermal/thermal_zone0/temp"
STANZA_TEMPLATE = ":{:9}:{}.{}"

class MemInfo(Mapping):
  _cache = None
  def __init__(self):
    if MemInfo._cache is not None:
      return

    clean = partial(re.compile('[^A-Za-z0-9]+').sub, '')
    MemInfo._cache = {}
    try:
      with open(MEMINFO_FILE, 'r') as mfd:
        for line in mfd:
          key, value, _ = line.split()
          MemInfo._cache[clean(key)] = int(value)
    except IOError:
      pass

  def __getitem__(self, key):
    return self._cache[key]

  def __iter__(self):
    return iter(self._cache)

  def __len__(self):
    return len(MemInfo._cache)


class TelemStatus(object):

  def __init__(self):
    try:
      with open(STATUS_FILE, 'rb') as sfd:
        self.st_data = pickle.loads(sfd.read())
    except IOError:
      self.st_data = dict(seq=0, timestamp=int(time.time()), rx_packets=0, tx_packets=0)

    self.st_data['seq'] = (self.st_data['seq'] % 999) + 1

  def __repr__(self):
    return "%s %s" % (self.__class__, self.st_data)

  def save(self):
    self.st_data['timestamp'] = int(time.time())
    try:
      with open(STATUS_FILE, 'wb') as sfd:
        sfd.write(pickle.dumps(self.st_data))
    except IOError as err:
      print(err)

  @property
  def sequence(self):
    return self.st_data['seq']

  @property
  def timestamp(self):
    return self.st_data['timestamp']

  @property
  def rx_packets(self):
    return self.st_data['rx_packets']

  @rx_packets.setter
  def rx_packets(self, value):
    self.st_data['rx_packets'] = value

  @property
  def tx_packets(self):
    return self.st_data['tx_packets']

  @tx_packets.setter
  def tx_packets(self, value):
    self.st_data['tx_packets'] = value



def get_default_iface():
  # We are interested by the fields
  # 0 = iface, 1 = dest, 3 = flags
  route = "/proc/net/route"
  try:
    with open(route, 'r') as rfd:
      for line in rfd:
        try:
          rinfo = line.strip().split()
          if rinfo[1] != '00000000' or not int(rinfo[3], 16) & 2:
            continue
          return rinfo[0]
        except KeyError:
          continue
  except IOError:
    return 'eth0'


def network_packets(iface):
  try:
    with open('/proc/net/dev', 'r') as ifd:
      for line in ifd:
        if line.find(iface) >= 0:
          data = line.split()
          break
      else:
        raise SystemError

    rx_packets, tx_packets = (data[2], data[10])
    return (int(rx_packets), int(tx_packets))
  except (IOError, ValueError, SystemError):
    return (0, 0)


def read_loadavg():
  try:
    with open(LOADAVG_FILE, 'r') as lfd:
      loadstr = lfd.readline()
  except IOError:
    return 0

  try:
    load15 = float(loadstr.split()[1])
  except ValueError:
    return 0

  return int(load15 * 1000)


def read_temperature():
  try:
    with open(THERMFILE) as tfd:
      _tmp = tfd.readline()
      temperature = int(_tmp.strip())
  except (IOError, ValueError):
    temperature = 0
  return temperature


def send_data(sequence, *data):
  data = data + (0,) * 5
  payload = ','.join([str(x) for x in data[:5]])
  print("T#{:03d},{},00000000".format(sequence, payload))


def aprs_send(call, key, *val):
  values = ','.join([str(x).strip() for x in val])
  stanza = STANZA_TEMPLATE.format(call, key, values)
  print(stanza)


def aprs_eqns(call, *coef):
  payload = coef + ((0, 1, 0),) * 5
  payload = list(itertools.chain.from_iterable(payload))
  aprs_send(call, "EQNS", *payload[:5*3])


def aprs_param(call, *val):
  payload = list(val) + ["Vx{}".format(i) for i in range(1, 5)]
  aprs_send(call, "PARM", *payload[:5])


def aprs_unit(call, *val):
  payload = val + ("U",) * 5
  aprs_send(call, "UNIT", *payload[:5])


def parse_arguments():
  """Parse the command arguments"""
  parser = ArgumentParser(description="APRS RaspberryPi temperature")
  parser.add_argument('-c', '--callsign', default=CALL_SIGN,
                      help='iGate full callsign [default: %(default)s')
  cmds = parser.add_mutually_exclusive_group(required=True)
  cmds.add_argument('-d', '--data', action="store_true",
                    help="Send the APRS data")
  cmds.add_argument('-e', '--eqns', action="store_true",
                    help="Send the APRS equation")
  cmds.add_argument('-p', '--param', action="store_true",
                    help="Send the APRS param")
  cmds.add_argument('-u', '--unit', action="store_true",
                    help="Send the APRS units")

  opts = parser.parse_args()
  return opts


def process_data():
  status = TelemStatus()
  memory = MemInfo()
  ifname = get_default_iface()
  (rx_packets, tx_packets) = network_packets(ifname)

  if status.rx_packets == 0:
    status.rx_packets = rx_packets
  if status.tx_packets == 0:
    status.tx_packets = tx_packets

  timelapse = 1 + int(time.time()) - status.timestamp

  rx_stat = int((rx_packets - status.rx_packets) / timelapse)
  tx_stat = int((tx_packets - status.tx_packets) / timelapse)

  send_data(status.sequence, read_loadavg(), read_temperature(),
            int(memory.get('MemFree', 0)) / 1024, rx_stat, tx_stat)

  status.rx_packets = rx_packets
  status.tx_packets = tx_packets
  status.save()


def main():
  opts = parse_arguments()

  if opts.param:
    aprs_param(opts.callsign, 'Cpu', 'Temp', 'FreeM', 'RxP', 'TxP')
  elif opts.unit:
    aprs_unit(opts.callsign, 'Load', 'DegC', 'Mb', 'Pkt', 'Pkt')
  elif opts.eqns:
    aprs_eqns(opts.callsign, (0, 0.001, 0), (0, 0.001, 0))
  elif opts.data:
    process_data()

if __name__ == "__main__":
  main()
