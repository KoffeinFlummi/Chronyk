#!/usr/bin/env python3

import os
import sys
import shutil
from setuptools import setup, find_packages

here = os.path.dirname(os.path.realpath(__file__))

def read(fname):
  return open(os.path.join(here, fname)).read()

setup(
  name = "Chronyk",
  version = "1.0",

  packages = ["chronyk"],
  install_requires = [],

  author = "Felix \"KoffeinFlummi\" Wiegand",
  author_email = "koffeinflummi@gmail.com",
  description = "A library for parsing human-written times and dates.",
  long_description = read("README.md"),
  license = "MIT",
  keywords = "time date clock human parser timezone",
  url = "https://github.com/KoffeinFlummi/PyGHI"
)
