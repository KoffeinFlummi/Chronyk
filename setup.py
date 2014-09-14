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
  version = "0.9",

  packages = ["chronyk"],
  install_requires = [],

  author = "Felix \"KoffeinFlummi\" Wiegand",
  author_email = "koffeinflummi@gmail.com",
  description = "A library for parsing human-written times and dates.",
  long_description = read("README.md"),
  license = "MIT",
  keywords = "time date clock human parser timezone",
  url = "https://github.com/KoffeinFlummi/PyGHI",
  classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4"
  ]
)
