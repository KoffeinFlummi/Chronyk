#!/usr/bin/env python3

"""Chronyk v1.0
=================================================

Human-written and human-readable dates and times.


Basic Usage:

# Input
>>> import chronyk
>>> t = chronyk.Chronyk("2014-06-01")
>>> t = chronyk.Chronyk("2 hours ago", allowFuture=False)
>>> t = chronyk.Chronyk(1410508814.295184, timezone=-3600)
>>> t = chronyk.Chronyk(somedatetimeobject)

# Output
>>> t.timestamp()
1410508814.295184
>>> t.timestring()
"2014-09-12 10:00:14"
>>> t.timestring("%Y-%m-%d")
"2014-09-12"
>>> t.ctime()
"Fri Sep 12 10:00:14 2014"
>>> t.relativestring()
"10 seconds ago"


More information can be found in the Readme in the repo linked below.

=================================================

Code can be found here:
https://github.com/KoffeinFlummi/Chronyk

LICENSE: MIT
Copyright 2014 Felix Wiegand
"""

__title__ = "Chronyk"
__version__ = "0.9"
__author__ = "Felix \"KoffeinFlummi\" Wiegand"
__license__ = "MIT"
__copyright__ = "Copyright 2014 Felix Wiegand"

from .chronyk import Chronyk, DateRangeError, LOCALTZ, currentutc
