#!/usr/bin/env python3

import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "Chronyk",
    version = "1.0",
    
    packages = ["chronyk"],
    install_requires = [],
    
    author = 'Felix "KoffeinFlummi" Wiegand',
    author_email = "koffeinflummi@gmail.com",
    description = "A library for parsing human-written times and dates.",
    long_description = read("README.rst"),
    license = "MIT",
    keywords = "time date clock human parser timezone",
    url = "https://github.com/KoffeinFlummi/Chronyk",
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
