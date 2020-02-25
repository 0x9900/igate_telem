#!/usr/bin/env python
#

from setuptools import setup
from igate_telem import __version__ as VERSION

setup(
  name="igate_telem",
  version=VERSION,
  license="BSD",
  description="Send igate or digipeater telemetry through APRS.",
  author="Fred C.",
  author_email="github-fred@hidzz.com",
  url="https://github.com/0x9900/igate_telem",
  packages=['igate'],
  entry_points={
    "console_scripts": ["igate_telem = igate:main"],
  },

)
