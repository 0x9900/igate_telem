#!/usr/bin/env python
#!/usr/bin/env python
#
# (C) 2019-2020 Fred C. (W6BSD)
# https://github.com/0x9900/fllog
#
# EQNS. is a, b, c | DisplayValue = a * val ^ 2 + b * val + c
# pylint: disable=missing-docstring

import itertools
import os
import re

from argparse import ArgumentParser
from collections import Mapping
from functools import partial

SEQUENCE_FILE = "/tmp/aprs_seq.dat"
LOADAVG_FILE = "/proc/loadavg"
MEMINFO_FILE = "/proc/meminfo"

CALL_SIGN = "W6BSD-5"
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

def get_sequence():
  try:
    if not os.path.exists(SEQUENCE_FILE):
      with open(SEQUENCE_FILE, 'a') as sfd:
        sfd.write("1")
        return 1
    else:
      with open(SEQUENCE_FILE, 'r+') as sfd:
        seq = int(sfd.read())
        seq = (seq % 999) + 1
        sfd.seek(0L)
        sfd.truncate()
        sfd.write(str(seq))
  except (IOError, ValueError):
    seq = 1
  return seq

def send_data(*data):
  sequence = get_sequence()
  data = data + (0,) * 5
  payload = ','.join([str(x) for x in data[:5]])
  print "T#{},{},00000000".format(sequence, payload)

def aprs_send(call, key, *val):
  values = ','.join([str(x).strip() for x in val])
  stanza = STANZA_TEMPLATE.format(call, key, values)
  print stanza

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

def main():
  opts = parse_arguments()
  memory = MemInfo()

  if opts.param:
    aprs_param(CALL_SIGN, 'Cpu', 'Temp', 'FreeM')
  elif opts.unit:
    aprs_unit(CALL_SIGN, 'Load', 'DegC', 'Mb')
  elif opts.eqns:
    aprs_eqns(CALL_SIGN, (0, 0.001, 0), (0, 0.001, 0))
  elif opts.data:
    send_data(read_loadavg(), read_temperature(), memory.get('MemFree', 0) / 1024)

if __name__ == "__main__":
  main()
