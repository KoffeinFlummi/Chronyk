#!/usr/bin/env python3

import re
import math
import time
import datetime
import calendar

LOCALTZ = time.timezone - 3600 * time.localtime().tm_isdst

def currentutc():
    """Returns the current UTC timestamp.

    This is important, since time.gmtime() seems to use time.timezone, which
    doesn't factor in DST and thus doesn't actually return a utc timestamp.
    """
    return time.time() + LOCALTZ

class DateRangeError(Exception):
    """Exception thrown when the value passed to the chronyk.Chronyk
    constructor exceeds the range permitted with allowpast and allowfuture.
    """
    pass

class Chronyk:
    """Class containing methods for parsing and outputting times and dates for
    humans. For usage information, consule the module documentation.

    :param timestr = current time
        This can be either a timestamp, a datetime object or a string
        describing a time or date.

    :param timezone = local timezone
        The timezone (in seconds west of UTC) the given time is in. By default,
        the local tz is used. To use UTC, use timezone=0.

    :param allowpast = True
        Determines if values from the past are allowed. This can be handy when
        parsing direct user input.

    :param allowfuture = True
        Determines if values from the future are allowed. This can be handy when
        parsing direct user input.

    If the passed values exceeds the bounds set by allowpast and allowfuture,
    a chronyk.DateRangeError is raised. If the type of the value is unknown to
    Chronyk, a TypeError is raised. If Chronyk fails to parse a given string, a
    ValueError is raised.
    """

    def __init__(
            self, timestr=None, timezone=LOCALTZ,
            allowpast=True, allowfuture=True):
        """ Converts input to UTC timestamp. """

        if timestr is None:
            timestr = time.time()
        self.timezone = timezone

        if type(timestr) == str:
            self.__timestamp__ = self.__fromstring__(timestr)

        elif type(timestr) in [int, float]:
            self.__timestamp__ = timestr + self.timezone

        elif type(timestr) in [
                datetime.datetime,
                datetime.date,
                datetime.time
            ]:
            self.__timestamp__ = time.mktime(timestr.timetuple())

        elif type(timestr) == time.struct_time:
            self.__timestamp__ = time.mktime(timestr) + self.timezone

        else:
            raise TypeError("Invalid type specified.")

        if not allowpast and self.__timestamp__ < currentutc():
            raise DateRangeError("Values from the past are not allowed.")
        if not allowfuture and self.__timestamp__ > currentutc():
            raise DateRangeError("Values from the future are not allowed.")

    def __fromrelative__(self, timestr):
        timestr = " {} ".format(timestr)

        if timestr.find(" ago ") == -1 and timestr.find(" in ") == -1:
            return None

        future = timestr.find(" in ") != -1
        coef = 1 if future else -1
        dati = datetime.datetime.utcnow()

        # timedelta does not support years
        if timestr.find(" year") != -1:
            try:
                match = re.match(r".*?([0-9]+?) year", timestr)
                assert not match is None
                dati = dati.replace(year=dati.year + int(match.group(1))*coef)
            except AssertionError:
                pass

        # ... or months
        if timestr.find(" month") != -1:
            try:
                match = re.match(r".*?([0-9]+?) month", timestr)
                assert not match is None
                months = int(match.group(1))
                newmonth = (((dati.month - 1) + months*coef) % 12) + 1
                newyear = dati.year + (((dati.month - 1) + months*coef) / 12)
                dati = dati.replace(year=int(newyear), month=int(newmonth))
            except AssertionError:
                pass
            # correct things like 31 Jan + 1 month => 31 Feb
            while dati.day > calendar.monthrange(dati.year, dati.month)[1]:
                dati = dati.replace(day=dati.day - 1)

        delta = {
            "weeks": 0,
            "days": 0,
            "hours": 0,
            "minutes": 0,
            "seconds": 0
        }

        for key in delta.keys():
            if timestr.find(" "+key[:-1]) != -1:
                try:
                    match = re.match(
                        re.compile(".*?([0-9]+?) "+key[:-1]),
                        timestr
                    )
                    assert not match is None
                    delta[key] += int(match.group(1))
                except AssertionError:
                    pass

        if not future:
            for key in delta.keys():
                delta[key] *= -1

        dati = dati + datetime.timedelta(**delta)

        return time.mktime(dati.timetuple())

    def __fromabsolute__(self, timestr):
        # http://en.wikipedia.org/wiki/Date_format_by_country
        datetimeformats = [
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S%Z",
            "%c",
            "%s"
        ]
        dateformats = [
            # ISO
            "%Y-%m-%d",
            # YMD other than ISO
            "%Y%m%d",
            "%Y.%m.%d",
            # DMY with full year
            "%d %m %Y",
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%d/%m %Y",
            "%d.%m.%Y",
            "%d. %m. %Y",
            "%d %b %Y",
            "%d %B %Y",
            "%d. %b %Y",
            "%d. %B %Y",
            # MDY with full year
            "%m/%d/%Y",
            "%b %d %Y",
            "%b %dst %Y",
            "%b %dnd %Y",
            "%b %drd %Y",
            "%b %dth %Y",
            "%b %d, %Y",
            "%b %dst, %Y",
            "%b %dnd, %Y",
            "%b %drd, %Y",
            "%b %dth, %Y",
            "%B %d %Y",
            "%B %dst %Y",
            "%B %dnd %Y",
            "%B %drd %Y",
            "%B %dth %Y",
            "%B %d, %Y",
            "%B %dst, %Y",
            "%B %dnd, %Y",
            "%B %drd, %Y",
            "%B %dth, %Y",
            # DMY with 2-digit year
            "%d %m %y",
            "%d-%m-%y",
            "%d/%m/%y",
            "%d/%m-%y", # why denmark?
            "%d.%m.%y",
            "%d. %m. %y",
            "%d %b %y",
            "%d %B %y",
            "%d. %b %y",
            "%d. %B %y",
            # MDY with 2-digit year
            "%m/%d/%y",
            "%b %dst %y",
            "%b %dnd %y",
            "%b %drd %y",
            "%b %dth %y",
            "%B %dst %y",
            "%B %dnd %y",
            "%B %drd %y",
            "%B %dth %y",
        ]
        timeformats = [
            # 24 hour clock with seconds
            "%H:%M:%S %z",
            "%H:%M:%S %z",
            "%H:%M:%S",
            # 24 hour clock without seconds
            "%H:%M %z",
            "%H:%M %Z",
            "%H:%M",
            # 12 hour clock with seconds
            "%I:%M:%S %p %z",
            "%I:%M:%S %p %Z",
            "%I:%M:%S %p",
            # 12 hour clock without seconds
            "%I:%M %p %z",
            "%I:%M %p %Z",
            "%I:%M %p"
        ]

        # Prepare combinations
        for dateformat in dateformats:
            for timeformat in timeformats:
                datetimeformats.append("{} {}".format(dateformat, timeformat))
            datetimeformats.append(dateformat)

        # Date / Datetime
        for dateformat in datetimeformats:
            try:
                struct = time.strptime(timestr, dateformat)
            except ValueError:
                pass
            else:
                timestamp = time.mktime(struct)
                if not "z" in dateformat.lower():
                    # string doesn't contains timezone information.
                    timestamp += self.timezone
                return timestamp

        # Time (using today as date)
        for timeformat in timeformats:
            timestr_full = time.strftime("%Y-%m-%d") + " " + timestr
            format_full = "%Y-%m-%d {}".format(timeformat)
            try:
                struct = time.strptime(timestr_full, format_full)
            except ValueError:
                pass
            else:
                timestamp = time.mktime(struct)
                if not "z" in timeformat.lower():
                    # string doesn't contains timezone information.
                    timestamp += self.timezone
                return timestamp

    def __fromstring__(self, timestr):
        timestr = timestr.lower().strip()

        # COMMON NAMES FOR TIMES
        if timestr in ["today", "now", "this week", "this month", "this day"]:
            return currentutc()
        if timestr in ["yesterday", "yester day"]:
            return currentutc() - 24*3600
        if timestr in ["yesteryear", "yester year"]:
            dati = datetime.datetime.utcnow()
            return time.mktime(dati.replace(year=dati.year-1).timetuple())

        # RELATIVE TIMES
        relative = self.__fromrelative__(timestr)
        if not relative is None:
            return relative

        # ABSOLUTE TIMES
        absolute = self.__fromabsolute__(timestr)
        if not absolute is None:
            return absolute

        raise ValueError("Failed to parse time string.")

    def __pluralstr__(self, string, value):
        if value == 1:
            return "1 {}".format(string)
        else:
            return "{} {}s".format(value, string)

    def datetime(self, timezone=None):
        """Returns a datetime object.

        This object retains all information, including timezones.

        :param timezone = self.timezone
            The timezone (in seconds west of UTC) to return the value in. By
            default, the timezone used when constructing the class is used
            (local one by default). To use UTC, use timezone = 0. To use the
            local tz, use timezone = chronyk.LOCALTZ.
        """
        if timezone is None:
            timezone = self.timezone
        return datetime.datetime.fromtimestamp(self.__timestamp__ - timezone)

    def timestamp(self, timezone=None):
        """Returns a timestamp (seconds since the epoch).

        :param timezone = self.timezone
            The timezone (in seconds west of UTC) to return the value in. By
            default, the timezone used when constructing the class is used
            (local one by default). To use UTC, use timezone = 0. To use the
            local tz, use timezone = chronyk.LOCALTZ.
        """
        if timezone is None:
            timezone = self.timezone
        return self.__timestamp__ - timezone

    def ctime(self, timezone=None):
        """Returns a ctime string.

        :param timezone = self.timezone
            The timezone (in seconds west of UTC) to return the value in. By
            default, the timezone used when constructing the class is used
            (local one by default). To use UTC, use timezone = 0. To use the
            local tz, use timezone = chronyk.LOCALTZ.
        """
        if timezone is None:
            timezone = self.timezone
        return time.ctime(self.__timestamp__ - timezone)

    def timestring(self, pattern="%Y-%m-%d %H:%M:%S", timezone=None):
        """Returns a time string.

        :param pattern = "%Y-%m-%d %H:%M:%S"
            The format used. By default, an ISO-type format is used. The
            syntax here is identical to the one used by time.strftime() and
            time.strptime().

        :param timezone = self.timezone
            The timezone (in seconds west of UTC) to return the value in. By
            default, the timezone used when constructing the class is used
            (local one by default). To use UTC, use timezone = 0. To use the
            local tz, use timezone = chronyk.LOCALTZ.
        """
        if timezone is None:
            timezone = self.timezone
        timestamp = self.__timestamp__ - timezone
        return time.strftime(pattern, time.gmtime(timestamp))

    def relativestring(
            self, now=None, minimum=10, maximum=3600*24*30,
            pattern="%Y-%m-%d", timezone=None):
        """Returns a relative time string (e.g. "10 seconds ago").

        :param now = time.time()
            The timestamp to compare this time to. By default, the current
            local time is used.

        :param minimum = 10
            Amount in seconds under which "just now" is returned instead of a
            numerical description. A value <= 0 disables this.

        :param maximum = 3600 * 24 * 30 (30 days)
            Amount in seconds above which the actual date is returned instead
            of a numerical description. A value < 0 disables this.

        :param pattern = "%Y-%m-%d"
            The string format to use when maximum is exceeded. The syntax here
            is identical to the one used by Chronyk.timestring(), which in turn
            is the same as the one used by time.strptime() and time.strftime().

        :param timezone = self.timezone
            The timezone (in seconds west of UTC) to return the result in. By
            default, the value used when constructing the class (local tz by
            default) is used. To use UTC, use timezone=0. To use the local TZ,
            use timezone=chronyk.LOCALTZ.
        """

        if now is None:
            now = time.time()
        if timezone is None:
            timezone = self.timezone

        diff = now - (self.__timestamp__ - timezone)
        future = diff < 0
        diff = abs(diff)

        if diff < minimum:
            return "just now"
        if diff > maximum and maximum > 0:
            return self.timestring(pattern)

        days = math.floor(diff / (24*3600))
        hours = math.floor((diff - (days*24*3600)) / 3600)
        minutes = math.floor((diff - (days*24*3600) - (hours*3600)) / 60)
        seconds = math.floor(diff-(days*24*3600)-(hours*3600)-(minutes*60))

        if days == 1:
            return "tomorrow" if future else "yesterday"

        mask = "in {}" if future else "{} ago"
        name = ""
        value = 0

        if days != 0:
            name = "day"
            value = days
        elif hours != 0:
            name = "hour"
            value = hours
        elif minutes != 0:
            name = "minute"
            value = minutes
        else:
            name = "second"
            value = seconds

        return mask.format(self.__pluralstr__(name, value))
