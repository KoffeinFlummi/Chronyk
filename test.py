#!/usr/bin/env python3

import os
import sys
import time

from chronyk import Chronyk

def main():
  assert(abs(time.time() - Chronyk().timestamp()) < 0.2)

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

  assert(Chronyk().ctime() == time.ctime(time.time()))
  assert(Chronyk(timezone=0).ctime() == time.ctime(time.mktime(time.gmtime()) + 3600 * time.localtime().tm_isdst))

  print("All tests successfull.")

if __name__ == "__main__":
  main()
