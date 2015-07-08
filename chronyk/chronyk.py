#!/usr/bin/env python3

import re
import math
import time
import collections
import datetime
import calendar

LOCALTZ = time.altzone


def _isdst(dt):
    """Check if date is in dst.
    """
    if type(dt) == datetime.date:
        dt = datetime.datetime.combine(dt, datetime.datetime.min.time())
    dtc = dt.replace(year=datetime.datetime.now().year)
    if time.localtime(dtc.timestamp()).tm_isdst == 1:
        return True
    return False


def _mktime(time_struct):
    """Custom mktime because Windows can't be arsed to properly do pre-Epoch
    dates, probably because it's busy counting all its chromosomes.
    """
    try:
        return time.mktime(time_struct)
    except OverflowError:
        dt = datetime.datetime(*time_struct[:6])
        ep = datetime.datetime(1970, 1, 1)
        diff = dt - ep
        ts = diff.days * 24 * 3600 + diff.seconds + time.timezone
        if time_struct.tm_isdst == 1:
            ts -= 3600
        # Guess if DST is in effect for -1
        if time_struct.tm_isdst == -1 and _isdst(dt):
            ts -= 3600
        return ts


def _strftime(pattern, time_struct=time.localtime()):
    """Custom strftime because Windows is shit again.
    """
    try:
        return time.strftime(pattern, time_struct)
    except OSError:
        dt = datetime.datetime.fromtimestamp(_mktime(time_struct))
        # This is incredibly hacky and will probably break with leap
        # year overlaps and shit. Any complaints should go here:
        # https://support.microsoft.com/
        original = dt.year
        current = datetime.datetime.now().year
        dt = dt.replace(year=current)
        ts = dt.timestamp()
        if _isdst(dt):
            ts -= 3600
        string = time.strftime(pattern, time.localtime(ts))
        string = string.replace(str(current), str(original))
        return string


def _gmtime(timestamp):
    """Custom gmtime because yada yada.
    """
    try:
        return time.gmtime(timestamp)
    except OSError:
        dt = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=timestamp)
        dst = int(_isdst(dt))
        return time.struct_time(dt.timetuple()[:8] + tuple([dst]))


def _dtfromtimestamp(timestamp):
    """Custom datetime timestamp constructor. because Windows. again.
    """
    try:
        return datetime.datetime.fromtimestamp(timestamp)
    except OSError:
        timestamp -= time.timezone
        dt = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=timestamp)
        if _isdst(dt):
            timestamp += 3600
            dt = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=timestamp)
        return dt


def _dfromtimestamp(timestamp):
    """Custom date timestamp constructor. ditto
    """
    try:
        return datetime.date.fromtimestamp(timestamp)
    except OSError:
        timestamp -= time.timezone
        d = datetime.date(1970, 1, 1) + datetime.timedelta(seconds=timestamp)
        if _isdst(d):
            timestamp += 3600
            d = datetime.date(1970, 1, 1) + datetime.timedelta(seconds=timestamp)
        return d


def currentutc():
    """Returns the current UTC timestamp.

    This is important, since time.gmtime() seems to use time.timezone, which
    doesn't factor in DST and thus doesn't actually return a utc timestamp.
    """
    return time.time() + LOCALTZ


def guesstype(timestr):
    """Tries to guess whether a string represents a time or a time delta and
    returns the appropriate object.

    :param timestr (required)
        The string to be analyzed
    """
    timestr_full = " {} ".format(timestr)
    if timestr_full.find(" in ") != -1 or timestr_full.find(" ago ") != -1:
        return Chronyk(timestr)

    comps = ["second", "minute", "hour", "day", "week", "month", "year"]
    for comp in comps:
        if timestr_full.find(comp) != -1:
            return ChronykDelta(timestr)

    return Chronyk(timestr)


def _round(num):
    """A custom rounding function that's a bit more 'strict'.
    """
    deci = num - math.floor(num)
    if deci > 0.8:
        return int(math.floor(num) + 1)
    else:
        return int(math.floor(num))


def _pluralstr(string, value):
    if value == 1:
        return "1 {}".format(string)
    else:
        return "{} {}s".format(value, string)


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
        Determines if values from the future are allowed. This can be handy
        when parsing direct user input.

    If the passed values exceeds the bounds set by allowpast and allowfuture,
    a chronyk.DateRangeError is raised. If the type of the value is unknown to
    Chronyk, a TypeError is raised. If Chronyk fails to parse a given string,
    a ValueError is raised.

    Subtracting Chronyk instances from another will yield a ChronykDelta
    object, which in turn can be added to other Chronyk instances.
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
                datetime.datetime, datetime.date, datetime.time]:
            self.__timestamp__ = _mktime(timestr.timetuple()) + self.timezone

        elif type(timestr) == time.struct_time:
            self.__timestamp__ = _mktime(timestr) + self.timezone

        else:
            raise TypeError("Failed to recognize given type.")

        if not allowpast and self.__timestamp__ < currentutc():
            raise DateRangeError("Values from the past are not allowed.")
        if not allowfuture and self.__timestamp__ > currentutc():
            raise DateRangeError("Values from the future are not allowed.")

    def __repr__(self):
        return "Chronyk({})".format(self.timestring())

    # Type Conversions
    def __str__(self):
        return self.timestring()

    def __int__(self):
        return int(self.timestamp(timezone=0))

    def __float__(self):
        return float(self.timestamp(timezone=0))

    # Comparison Operators
    def __eq__(self, other):
        if type(other) == Chronyk:
            return self.__timestamp__ == other.timestamp(timezone=0)
        if type(other) in [int, float]:
            return self.__timestamp__ == other

        return NotImplemented

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        if type(other) == Chronyk:
            return self.__timestamp__ > other.timestamp(timezone=0)
        if type(other) in [int, float]:
            return self.__timestamp__ > other

        return NotImplemented

    def __le__(self, other):
        return not self.__gt__(other)

    def __lt__(self, other):
        if type(other) == Chronyk:
            return self.__timestamp__ < other.timestamp(timezone=0)
        if type(other) in [int, float]:
            return self.__timestamp__ < other

        return NotImplemented

    def __ge__(self, other):
        return not self.__lt__(other)

    # Arithmetic Operators
    def __add__(self, other):
        if type(other) == ChronykDelta:
            newtimest = self.timestamp() + other.seconds
            return Chronyk(newtimest, timezone=self.timezone)
        if type(other) in [int, float]:
            newtimest = self.timestamp() + other
            return Chronyk(newtimest, timezone=self.timezone)

        return NotImplemented

    def __sub__(self, other):
        if type(other) == Chronyk:
            delta = self.__timestamp__ - other.timestamp(timezone=0)
            return ChronykDelta(delta)
        if type(other) == ChronykDelta:
            newtimest = self.timestamp() - other.seconds
            return Chronyk(newtimest, timezone=self.timezone)
        if type(other) in [int, float]:
            newtimest = self.timestamp() - other
            return Chronyk(newtimest, timezone=self.timezone)

        return NotImplemented

    # Helpers
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
                assert match is not None
                dati = dati.replace(
                    year=dati.year + int(match.group(1)) * coef
                )
            except AssertionError:
                pass

        # ... or months
        if timestr.find(" month") != -1:
            try:
                match = re.match(r".*?([0-9]+?) month", timestr)
                assert match is not None
                months = int(match.group(1))
                newyear = dati.year + int(((dati.month - 1) + months * coef) / 12)
                newmonth = (((dati.month - 1) + months * coef) % 12) + 1
                newday = dati.day
                while newday > calendar.monthrange(newyear, newmonth)[1]:
                    newday -= 1
                dati = dati.replace(year=newyear, month=newmonth, day=newday)
            except AssertionError:
                pass

        delta = {
            "weeks": 0,
            "days": 0,
            "hours": 0,
            "minutes": 0,
            "seconds": 0
        }

        for key in delta.keys():
            if timestr.find(" " + key[:-1]) != -1:
                try:
                    match = re.match(
                        re.compile(".*?([0-9]+?) " + key[:-1]),
                        timestr
                    )
                    assert match is not None
                    delta[key] += int(match.group(1))
                except AssertionError:
                    pass

        if not future:
            for key in delta.keys():
                delta[key] *= -1

        dati = dati + datetime.timedelta(**delta)

        return _mktime(dati.timetuple())

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
            # Popular MDY formats
            "%m/%d/%Y",
            "%m/%d/%y",
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
            "%d/%m-%y",  # why denmark?
            "%d.%m.%y",
            "%d. %m. %y",
            "%d %b %y",
            "%d %B %y",
            "%d. %b %y",
            "%d. %B %y",
            # MDY with 2-digit year
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
                timestamp = _mktime(struct)
                if "z" not in dateformat.lower():
                    # string doesn't contains timezone information.
                    timestamp += self.timezone
                return timestamp

        # Time (using today as date)
        for timeformat in timeformats:
            timestr_full = _strftime("%Y-%m-%d") + " " + timestr
            format_full = "%Y-%m-%d {}".format(timeformat)
            try:
                struct = time.strptime(timestr_full, format_full)
            except ValueError:
                pass
            else:
                timestamp = _mktime(struct)
                if "z" not in timeformat.lower():
                    # string doesn't contains timezone information.
                    timestamp += self.timezone
                return timestamp

    def __fromstring__(self, timestr):
        timestr = timestr.lower().strip().replace(". ", " ")

        # COMMON NAMES FOR TIMES
        if timestr in ["today", "now", "this week", "this month", "this day"]:
            return currentutc()
        if timestr in ["yesterday", "yester day"]:
            return currentutc() - 24 * 3600
        if timestr in ["yesteryear", "yester year"]:
            dati = datetime.datetime.utcnow()
            return _mktime(dati.replace(year=dati.year - 1).timetuple())

        # RELATIVE TIMES
        relative = self.__fromrelative__(timestr)
        if relative is not None:
            return relative

        # ABSOLUTE TIMES
        absolute = self.__fromabsolute__(timestr)
        if absolute is not None:
            return absolute

        raise ValueError("Failed to parse time string.")

    # Methods
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
        return _dtfromtimestamp(self.__timestamp__ - timezone)
        
    def date(self, timezone=None):
        """Returns a datetime.date object.
        This object retains all information, including timezones.
        
        :param timezone = self.timezone
            The timezone (in seconds west of UTC) to return the value in. By
            default, the timezone used when constructing the class is used
            (local one by default). To use UTC, use timezone = 0. To use the
            local tz, use timezone = chronyk.LOCALTZ.
        """
        if timezone is None:
            timezone = self.timezone
        return _dfromtimestamp(self.__timestamp__ - timezone)

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
        timestamp -= LOCALTZ
        return _strftime(pattern, _gmtime(timestamp))

    def relativestring(
            self, now=None, minimum=10, maximum=3600 * 24 * 30,
            pattern="%Y-%m-%d", timezone=None, maxunits=1):
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

        :param maxunits = 1
            The maximum amount of units to return. This is identical to the
            parameter of the same name of ChronykDelta's timestring method.
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

        timestring = ChronykDelta(diff).timestring(maxunits=maxunits)
        if timestring == "1 day":
            return "tomorrow" if future else "yesterday"

        if future:
            return "in {}".format(timestring)
        else:
            return "{} ago".format(timestring)


class ChronykDelta:
    """Abstraction for a certain amount of time.

    :param timestr (required)
        The amount of time to represent. This can be either a number
        (int / float) or a string, which will be parsed accordingly.

    If you supply an unknown type, a TypeError is raised. If the string you
    passed cannot be parsed, a ValueError is raised.
    """

    def __init__(self, timestr):
        if type(timestr) == str:
            self.seconds = self.__fromstring__(timestr)
        elif type(timestr) in [int, float]:
            self.seconds = timestr
        else:
            raise TypeError("Failed to recognize given type.")

    def __repr__(self):
        return "ChronykDelta({})".format(self.timestring())

    # Type Conversions
    def __str__(self):
        return self.timestring()

    def __int__(self):
        return int(self.seconds)

    def __float__(self):
        return float(self.seconds)

    # Comparison Operators
    def __eq__(self, other):
        if type(other) == ChronykDelta:
            return self.seconds == other.seconds
        if type(other) in [int, float]:
            return self.seconds == other

        return NotImplemented

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        if type(other) == ChronykDelta:
            return self.seconds > other.seconds
        if type(other) in [int, float]:
            return self.seconds > other

        return NotImplemented

    def __le__(self, other):
        return not self.__gt__(other)

    def __lt__(self, other):
        if type(other) == ChronykDelta:
            return self.seconds < other.seconds
        if type(other) in [int, float]:
            return self.seconds < other

        return NotImplemented

    def __ge__(self, other):
        return not self.__lt__(other)

    # Arithmetic Operators
    def __add__(self, other):
        if type(other) == ChronykDelta:
            return ChronykDelta(self.seconds + other.seconds)
        if type(other) == Chronyk:
            return other + self
        if type(other) in [int, float]:
            return ChronykDelta(self.seconds + other)

        return NotImplemented

    def __sub__(self, other):
        if type(other) == ChronykDelta:
            return ChronykDelta(self.seconds - other.seconds)
        if type(other) in [int, float]:
            return ChronykDelta(self.seconds - other)

        return NotImplemented

    def __mul__(self, other):
        if type(other) in [int, float]:
            return ChronykDelta(self.seconds * other)

        return NotImplemented

    def __truediv__(self, other):
        if type(other) in [int, float]:
            return ChronykDelta(self.seconds / other)

        return NotImplemented

    def __floordiv__(self, other):
        if type(other) in [int, float]:
            return int(self.__truediv__(other))

        return NotImplemented

    # Methods
    def __fromstring__(self, timestr):
        seconds = 0

        comps = {
            "second": 1,
            "minute": 60,
            "hour": 3600,
            "day": 3600 * 24,
            "week": 3600 * 24 * 7,
            "month": 3600 * 24 * 30,
            "year": 3600 * 24 * 365
        }

        for k, v in comps.items():
            try:
                match = re.match(
                    re.compile(".*?([0-9]+?) "+k),
                    timestr
                )
                assert match is not None
                seconds += float(match.group(1)) * v
            except AssertionError:
                pass

        return seconds

    def timestring(self, maxunits=3):
        """Returns a string representation of this amount of time, like:
        "2 hours and 30 minutes" or "4 days, 2 hours and 40 minutes"

        :param maxunits = 3
            The maximum amount of units to use.

            1: "2 hours"
            4: "4 days, 2 hours, 5 minuts and 46 seconds"

        This method ignores the sign of the amount of time (that rhimes).
        """

        try:
            assert maxunits >= 1
        except:
            raise ValueError("Values < 1 for maxunits are not supported.")

        values = collections.OrderedDict()

        seconds = abs(self.seconds)

        values["year"] = _round(seconds / (3600 * 24 * 365))
        values["year"] = values["year"] if values["year"] > 0 else 0
        seconds -= values["year"] * 3600 * 24 * 365

        values["month"] = _round(seconds / (3600 * 24 * 30))
        values["month"] = values["month"] if values["month"] > 0 else 0
        seconds -= values["month"] * 3600 * 24 * 30

        values["day"] = _round(seconds / (3600 * 24))
        values["day"] = values["day"] if values["day"] > 0 else 0
        seconds -= values["day"] * 3600 * 24

        values["hour"] = _round(seconds / 3600)
        values["hour"] = values["hour"] if values["hour"] > 0 else 0
        seconds -= values["hour"] * 3600

        values["minute"] = _round(seconds / 60)
        values["minute"] = values["minute"] if values["minute"] > 0 else 0
        values["second"] = _round(seconds - values["minute"] * 60)

        for k, v in values.items():
            if v == 0:
                values.pop(k)
            else:
                break

        textsegs = []
        for k, v in list(values.items())[:maxunits]:
            if v > 0:
                textsegs.append(_pluralstr(k, v))

        if len(textsegs) == 0:
            return ""
        if len(textsegs) == 1:
            return textsegs[0]

        return ", ".join(textsegs[:-1]) + " and " + textsegs[-1]
