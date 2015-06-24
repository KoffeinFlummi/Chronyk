#!/usr/bin/env python3

import pytest

import sys
import time
import calendar
import datetime

from chronyk import LOCALTZ, Chronyk, ChronykDelta, currentutc, guesstype, DateRangeError

def isEqual(time1, time2):
    return abs(time1 - time2) < 0.1

###############################################################################

def test_currentutc():
    currentutc()

def test_guesstype():
    assert guesstype(9001) == Chronyk(9001)
    assert guesstype("2 hours ago").relativestring() == Chronyk("2 hours ago").relativestring()
    assert guesstype("2 hours") == ChronykDelta("2 hours")

def test_empty_con():
    assert isEqual(Chronyk().timestamp(), time.time())

def test_none_con():
    assert isEqual(Chronyk(None).timestamp(), Chronyk(time.time()).timestamp())

def test_common_strings():
    c1 = Chronyk("today").relativestring()
    c2 = Chronyk("now").relativestring()
    c3 = Chronyk("this week").relativestring()
    c4 = Chronyk("this month").relativestring()
    c5 = Chronyk("this day").relativestring()
    assert c1 == c2 and c2 == c3 and c3 == c4 and c4 == c5

def test_yesterday():
    assert Chronyk("yesterday").relativestring() == "yesterday"

def test_yesteryear():
    assert Chronyk("yesteryear").relativestring() == Chronyk("1 year ago").relativestring()

# TEST PRE-EPOCH DATES

def test_pre_epoch_1():
    assert Chronyk(datetime.datetime(1950, 1, 1)).datetime() == datetime.datetime(1950, 1, 1)

def test_pre_epoch_2():
    assert Chronyk(time.strptime("1950 01 01", "%Y %m %d")).timestring("%Y %m %d") == "1950 01 01"

# ABSOLUTE STRINGS

def test_absolute_iso():
    t = Chronyk("2014-09-18 11:24:47")
    assert t.ctime() == "Thu Sep 18 11:24:47 2014"

def test_absolute_iso_date():
    t = Chronyk("2014-09-18")
    assert t.ctime() == "Thu Sep 18 00:00:00 2014"

def test_absolute_written_1():
    t = Chronyk("May 2nd, 2015")
    assert t.ctime() == "Sat May  2 00:00:00 2015"

def test_absolute_written_2():
    t = Chronyk("2. August 2010")
    assert t.ctime() == "Mon Aug  2 00:00:00 2010"

def test_absolute_12hr():
    t = Chronyk("11:14 am")
    assert t.ctime()[11:-5] == "11:14:00"

def test_absolute_12hr_seconds():
    t = Chronyk("11:14:32 am")
    assert t.ctime()[11:-5] == "11:14:32"

def test_absolute_24hr():
    t = Chronyk("17:14")
    assert t.ctime()[11:-5] == "17:14:00"

def test_absolute_24hr_seconds():
    t = Chronyk("17:14:32")
    assert t.ctime()[11:-5] == "17:14:32"

def test_absolute_value():
    with pytest.raises(ValueError):
        Chronyk("warglblargl")

# RELATIVE STRINGS

def test_relative_now():
    assert Chronyk().relativestring() == "just now"

def test_relative_seconds_1():
    assert Chronyk("2 seconds ago").relativestring() == "just now"

def test_relative_seconds_2():
    assert Chronyk("in 5 seconds").relativestring() == "just now"

def test_relative_seconds_3():
    timest = time.time()
    assert Chronyk(timest - 5).relativestring(now=timest, minimum=0) == "5 seconds ago"

def test_relative_minutes_1():
    assert Chronyk("1 minute ago").relativestring() == "1 minute ago"

def test_relative_minutes_2():
    assert Chronyk("in 2 minutes").relativestring() == "in 2 minutes"

def test_relative_hours_1():
    assert Chronyk("1 hour ago").relativestring() == "1 hour ago"

def test_relative_hours_2():
    assert Chronyk("in 2 hours").relativestring() == "in 2 hours"

def test_relative_days_1():
    assert Chronyk("10 days ago").relativestring() == "10 days ago"

def test_relative_days_2():
    assert Chronyk("in 20 days").relativestring() == "in 20 days"

def test_relative_weeks_1():
    assert Chronyk("1 week ago").relativestring() == "7 days ago"

def test_relative_weeks_2():
    assert Chronyk("in 2 weeks").relativestring() == "in 14 days"

def test_relative_weeks_3():
    assert Chronyk("in blurgh weeks and 2 days").relativestring() == "in 2 days"

def test_relative_months_1():
    assert Chronyk("overninethousand months and 2 days ago").relativestring() == "2 days ago"

def test_relative_months_2():
    dati = datetime.datetime.utcnow()
    newmonth = (((dati.month - 1) + 4) % 12) + 1
    newyear = dati.year + int(((dati.month - 1) + 4) / 12)
    newday = dati.day
    while newday > calendar.monthrange(newyear, newmonth)[1]:
        newday -= 1
    dati = dati.replace(year=newyear, month=newmonth, day=newday)
    timestr = time.strftime("%Y-%m-%d", dati.timetuple())
    assert Chronyk("in 4 months", timezone=0).relativestring() == timestr

def test_relative_years_1():
    assert Chronyk("something years and 2 days ago").relativestring() == "2 days ago"

def test_relative_years_2():
    dati = datetime.datetime.utcnow()
    dati = dati.replace(year=dati.year - 2)
    timestr = time.strftime("%Y-%m-%d", dati.timetuple())
    assert Chronyk("2 years ago").relativestring() == timestr

def test_struct():
    timestr = time.localtime()
    assert Chronyk(timestr).timestamp() == time.mktime(timestr)

def test_valid_1():
    Chronyk("2 hours ago", allowfuture=False, allowpast=True)

def test_valid_2():
    Chronyk("in 2 hours", allowfuture=True, allowpast=False)

def test_valid_3():
    with pytest.raises(DateRangeError):
        Chronyk("2 hours ago", allowpast=False)

def test_valid_4():
    with pytest.raises(DateRangeError):
        Chronyk("in 2 hours", allowfuture=False)

def test_typeerror():
    with pytest.raises(TypeError):
        Chronyk(["this", "should", "throw", "TypeError"])

def test_datetime():
    timest = currentutc()
    assert Chronyk(timest, timezone=0).datetime() == datetime.datetime.fromtimestamp(timest)
    
def test_date():
    timest = currentutc()
    assert Chronyk(timest, timezone=0).date() == datetime.date.fromtimestamp(timest)

def test_timest_1():
    timest = time.time()
    assert Chronyk(timest).timestamp() == timest

def test_timest_2():
    timest = time.time()
    assert Chronyk(timest, timezone=0).timestamp(timezone=-7200) == timest + 7200

def test_timest_3():
    timest = time.time()
    assert Chronyk(timest, timezone=-7200).timestamp(timezone=0) == timest - 7200

def test_timestring_1():
    timest = time.time()
    assert Chronyk(timest).timestring() == time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(timest - LOCALTZ))

def test_timestring_2():
    timest = time.time()
    assert Chronyk(timest).timestring("%Y-%m-%d") == time.strftime("%Y-%m-%d", time.gmtime(timest - LOCALTZ))

def test_operators_eq():
    timest = time.time()
    assert Chronyk(timest) - 5 == Chronyk(timest - 5) and Chronyk(timest, timezone=0) == timest

def test_operators_str():
    t = Chronyk()
    assert str(t) == t.timestring()

def test_operators_num():
    timest = time.time()
    t = Chronyk(timest, timezone=0)
    assert int(timest) == int(t) and int(t) == int(float(t))

def test_operators_ne():
    timest = time.time()
    assert Chronyk(timest) != Chronyk(timest - 2)

def test_operators_ltgt():
    timest = time.time()
    assert Chronyk(timest) > Chronyk(timest - 5)
    assert Chronyk(timest, timezone=0) > timest - 5
    assert Chronyk(timest) < Chronyk(timest + 5)
    assert Chronyk(timest, timezone=0) < timest + 5
    assert Chronyk(timest) <= Chronyk(timest)
    assert Chronyk(timest, timezone=0) <= timest
    assert Chronyk(timest) >= Chronyk(timest - 5)
    assert Chronyk(timest, timezone=0) >= timest - 5

def test_operators_add():
    timest = time.time()
    assert Chronyk(timest) + ChronykDelta(5) == Chronyk(timest + 5)
    assert Chronyk(timest) + 5 == Chronyk(timest + 5)

def test_operators_sub():
    timest = time.time()
    assert Chronyk(timest) - Chronyk(timest - 5) == ChronykDelta(5)
    assert Chronyk(timest) - ChronykDelta(5) == Chronyk(timest - 5)
    assert Chronyk(timest, timezone=0) - 5 == timest - 5

def test_delta_type():
    with pytest.raises(TypeError):
        ChronykDelta(["WEEE", "EEEEE", "EEEEEE"])

def test_delta_timestring_1():
    assert ChronykDelta("5 hours").timestring() == "5 hours"

def test_delta_timestring_2():
    assert ChronykDelta("1 week").timestring() == "7 days"

def test_delta_timestring_3():
    assert ChronykDelta("1 hour").timestring() == "1 hour"

def test_delta_timestring_4():
    assert ChronykDelta("1 day and 12 hours").timestring() == "1 day and 12 hours"

def test_delta_timestring_5():
    assert ChronykDelta("1 day and 12 hours").timestring(maxunits=1) == "1 day"

def test_delta_timestring_6():
    with pytest.raises(ValueError):
        ChronykDelta("1 day ago").timestring(maxunits=0)

def test_delta_timestring_7():
    assert ChronykDelta(0).timestring() == ""

def test_delta_operators_str():
    assert ChronykDelta(5).timestring() == str(ChronykDelta(5))

def test_delta_operators_num():
    assert 5 == int(ChronykDelta(5)) and int(ChronykDelta(5)) == float(ChronykDelta(5))

def test_delta_operators_eq():
    assert ChronykDelta(5) == ChronykDelta(5) and ChronykDelta(5) == 5

def test_delta_operators_neq():
    assert ChronykDelta(5) != ChronykDelta(6) and ChronykDelta(5) != 3

def test_delta_operators_ltgt():
    assert ChronykDelta(5) > ChronykDelta(4) and ChronykDelta(5) > 3
    assert ChronykDelta(5) < ChronykDelta(7) and ChronykDelta(5) < 9
    assert ChronykDelta(5) >= ChronykDelta(5) and ChronykDelta(5) >= 3
    assert ChronykDelta(5) <= 5 and ChronykDelta(5) <= ChronykDelta(6)

def test_delta_operators_add():
    timest = time.time()
    assert ChronykDelta(5) + ChronykDelta(-5) == 0
    assert ChronykDelta(5) + Chronyk(timest) == Chronyk(timest + 5)
    assert ChronykDelta(5) + 10 == 15

def test_delta_operators_sub():
    assert ChronykDelta(5) - 5 == 0
    assert ChronykDelta(5) - ChronykDelta(1) == 4

def test_delta_operators_mul():
    assert ChronykDelta(12) * 2 == 24

def test_delta_operators_div():
    assert ChronykDelta(10) / 2 == 5

if __name__ == "__main__":
    sys.exit(pytest.main())
