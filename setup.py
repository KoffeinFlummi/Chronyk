#!/usr/bin/env python3

from setuptools import setup

setup(
  name = "Chronyk",
  version = "0.9.1",

  packages = ["chronyk"],
  install_requires = [],

  author = "Felix \"KoffeinFlummi\" Wiegand",
  author_email = "koffeinflummi@gmail.com",
  description = "A library for parsing human-written times and dates.",
  long_description = """
A small Python 3 library containing some handy tools for handling time,
especially when it comes to interfacing with those pesky humans.

Features
--------

-  Parsing human-written strings ("10 minutes ago", "10. April 2015",
   "2014-02-15"...)
-  Relative time string creation ("in 2 hours", "5 hours ago")
-  Various input formats
-  Easy to use

Installation
------------

::

    $ pip install chronyk

Usage
-----

**Basic:**

::

    >>> from chronyk import Chronyk
    >>> t = Chronyk(1410531179.0)
    >>> t = Chronyk("May 2nd, 2016 12:51 am")
    >>> t = Chronyk("yesterday")
    >>> t = Chronyk("21. 8. 1976 23:18")
    >>> t = Chronyk("2 days and 30 hours ago")
    >>> t.ctime()
    'Tue Sep  9 05:59:39 2014'
    >>> t.timestamp()
    1410235179.0
    >>> t.timestring()
    '2014-09-09 05:59:39'
    >>> t.timestring("%Y-%m-%d")
    '2014-09-09'
    >>> t.relativestring()
    '3 days ago'

**Input validation:**

::

    import sys
    import chronyk

    timestr = input("Please enter the date you were born: ")
    try:
        date = chronyk.Chronyk(timestr, allowfuture=False)
    except chronyk.DateRangeError:
        print("Yeah, right.")
        sys.exit(1)
    except ValueError:
        print("Failed to parse birthdate.")
        sys.exit(1)
    else:
        print("You were born {}".format(date.relativestring()))

**Timezones:**

By default, the Chronyk constructor uses local time, and every method by
default uses whatever was passed to the constructor as well.

Almost all methods, however, have a timezone keyargument that you can
use to define your local offset from UTC in seconds (positive for west,
negative for east).

If you want to use a certain timezone for more than one method, you can
also change the ``timezone`` instance attribute itself:

::

    >>> t = Chronyk("4 hours ago", timezone=0) # using UTC
    >>> t.ctime()
    'Tue Sep  9 10:53:42 2014'
    >>> t.timezone = -3600 # changes to CET (UTC+1)
    >>> t.relativeTime()
    '5 hours ago'
    >>> t.ctime()
    'Tue Sep  9 09:53:42 2014'


This uses the local relative time and returns a time string relative to
current UTC:

::

    >>> t = Chronyk("4 hours ago")
    >>> t.relativestring(timezone=0)
    '3 hours ago'


This uses a UTC timestamp and returns a time string relative to local
time:

::

    >>> t = Chronyk(1410524713.69, timezone=0)
    >>> t.relativestring(timezone=chronyk.LOCALTZ)
    '2 hours ago'
""",
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
