#!/usr/bin/env python3

import os
import sys
import time

from chronyk import LOCALTZ, Chronyk, currentutc, DateRangeError

def isEqual(time1, time2):
  return abs(time1 - time2) < 0.1

def main():
  currentutc()

  # Constructor - None / Timestamp
  assert(isEqual(Chronyk().timestamp(), time.time()))
  assert(isEqual(Chronyk(None).timestamp(), Chronyk(time.time()).timestamp()))

  # Constructor - Common Strings
  c1 = Chronyk("today").relativestring()
  c2 = Chronyk("now").relativestring()
  c3 = Chronyk("this week").relativestring()
  c4 = Chronyk("this month").relativestring()
  c5 = Chronyk("this day").relativestring()
  assert(c1 == c2 and c2 == c3 and c3 == c4 and c4 == c5)
  assert(Chronyk("yesterday").relativestring() == "yesterday")
  assert(Chronyk("yesteryear").relativestring() == Chronyk("1 year ago").relativestring())

  # Constructor - Absolute Strings
  t = Chronyk("2014-09-18 11:24:47")
  assert(t.ctime() == "Thu Sep 18 11:24:47 2014")
  t = Chronyk("2014-09-18")
  assert(t.ctime() == "Thu Sep 18 00:00:00 2014")
  t = Chronyk("May 2nd, 2015")
  assert(t.ctime() == "Sat May  2 00:00:00 2015")
  t = Chronyk("2. August 2010")
  assert(t.ctime() == "Mon Aug  2 00:00:00 2010")
  t = Chronyk("11:14 am")
  assert(t.ctime()[11:-5] == "11:14:00")
  t = Chronyk("11:14:32 am")
  assert(t.ctime()[11:-5] == "11:14:32")
  t = Chronyk("17:14")
  assert(t.ctime()[11:-5] == "17:14:00")
  t = Chronyk("17:14:32")
  assert(t.ctime()[11:-5] == "17:14:32")

  # Constructor - Relative Strings
  assert(Chronyk().relativestring() == "just now")
  assert(Chronyk("2 seconds ago").relativestring() == "just now")
  assert(Chronyk("in 5 seconds").relativestring() == "just now")
  assert(Chronyk("1 minute ago").relativestring() == "1 minute ago")
  assert(Chronyk("in 2 minutes and 30 seconds").relativestring() == "in 2 minutes")
  assert(Chronyk("1 hour ago").relativestring() == "1 hour ago")
  assert(Chronyk("in 2 hours and 10 seconds").relativestring() == "in 2 hours")
  assert(Chronyk("10 days ago").relativestring() == "10 days ago")
  assert(Chronyk("in 20 days and 5 minutes").relativestring() == "in 20 days")
  assert(Chronyk("1 week ago").relativestring() == "7 days ago")
  assert(Chronyk("in 2 weeks and 1 hour").relativestring() == "in 14 days")

  # Constructor - Struct time
  timestr = time.localtime()
  assert(Chronyk(timestr).timestamp() == time.mktime(timestr))

  # Constructor - date range validation
  Chronyk("2 hours ago", allowfuture=False, allowpast=True)
  Chronyk("in 2 hours", allowfuture=True, allowpast=False)
  try:
    Chronyk("2 hours ago", allowpast=False)
  except DateRangeError:
    pass
  else:
    raise DateRangeError
  try:
    Chronyk("in 2 hours", allowfuture=False)
  except DateRangeError:
    pass
  else:
    raise DateRangeError

  # Timestamp
  tstamp = time.time()
  assert(Chronyk(tstamp).timestamp() == tstamp)
  assert(Chronyk(tstamp, timezone=0).timestamp(timezone=-7200) == tstamp + 7200)
  assert(Chronyk(tstamp, timezone=-7200).timestamp(timezone=0) == tstamp - 7200)

  # Timestring
  timest = time.time()
  assert(Chronyk(timest).timestring() == time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(timest)))
  assert(Chronyk(timest).timestring("%Y-%m-%d") == time.strftime("%Y-%m-%d", time.gmtime(timest)))

  print("All tests successfull.")

if __name__ == "__main__":
  main()
