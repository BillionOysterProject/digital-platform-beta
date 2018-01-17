from __future__ import absolute_import
import datetime
from dateutil import tz, parser
import pytz
import time
import re
import six

RX_PANDAS_TIMESTR = re.compile(
    '(?P<value>\d+)\s*(?P<unit>(?:YEARS?|YRS?|MONTHS?|DAYS?|HOURS?|HRS?|MINUTES?|MINS?|SECONDS?|SECS?|MS|US|NS|[AYMDHTSLUN]))'  # noqa
)

PANDAS_UNITS = 'AMDHTSLUN'

RX_SPACE = re.compile('\s+')
PANDAS_TO_ATTR = {
    'A':       'from_years',
    'Y':       'from_years',
    'YR':      'from_years',
    'YRS':     'from_years',
    'YEAR':    'from_years',
    'YEARS':   'from_years',
    'M':       'from_months',
    'MONTH':   'from_months',
    'MONTHS':  'from_months',
    'D':       'from_days',
    'DAY':     'from_days',
    'DAYS':    'from_days',
    'H':       'from_hours',
    'HR':      'from_hours',
    'HRS':     'from_hours',
    'HOUR':    'from_hours',
    'HOURS':   'from_hours',
    'T':       'from_minutes',
    'MIN':     'from_minutes',
    'MINS':    'from_minutes',
    'MINUTE':  'from_minutes',
    'MINUTES': 'from_minutes',
    'S':       'from_seconds',
    'SEC':     'from_seconds',
    'SECS':    'from_seconds',
    'SECOND':  'from_seconds',
    'SECONDS': 'from_seconds',
    'L':       'from_milliseconds',
    'MS':      'from_milliseconds',
    'U':       'from_microseconds',
    'US':      'from_microseconds',
    'N':       'from_nanoseconds',
    'NS':      'from_nanoseconds',
}


class Time(object):
    NATIVE_DATETIME_TYPES = tuple([
        datetime.datetime,
        datetime.date,
        datetime.timedelta,
    ])

    """
    Time is a wrapper for various useful datetime operations for metrics.

    Arguments:

    - **tm** (`int`, `datetime.datetime`, `datetime.timedelta`, `str`, `Time`):

        If given as an `int`, the number will be interpreted as epoch nanoseconds.

        If given as a `datetime.datetime` or `Time`, the instance will be created to
        represent the same time as that object.

        If given as a `datetime.timedelta`, the instance will be created with this
        offset applied to the epoch (1970-01-01 00:00:00 UTC).

        If given as a `str`, the string will be interpreted as a Pandas time string.

    Usage:

    ```
    >>> metric_time = Time(datetime.datetime.now())
    >>> str(metric_time)
    2017-05-19T10:17:23.356527
    >>> metric_time.total_seconds()
    1495105079906092000
    ```

    ```
    >>> metric_timedelta = Time(datetime.timedelta(days=100))
    >>> metric_time.freq
    100D
    >>> metric_time.total_seconds()
    8640000000000000
    ```

    ```
    >>> metric_timedelta = Time('3A 4M 27D')
    >>> metric_time.freq
    100D
    >>> metric_time.total_seconds()
    8640000000000000
    ```
    """
    def __init__(self, tm=None):
        self._nanoseconds = 0

        if isinstance(tm, self.NATIVE_DATETIME_TYPES):
            self._parse(tm)
        elif isinstance(tm, six.string_types):
            if '-' in tm and not tm.startswith('-'):
                self._parse(parser.parse(tm))
            elif tm.startswith('+'):
                self._nanoseconds = (Time() + self.from_pandas_string(tm))._nanoseconds
            else:
                self._nanoseconds = self.from_pandas_string(tm)._nanoseconds
        elif isinstance(tm, (int, float, long)):
            self._nanoseconds = long(tm)
        elif tm is None:
            self._nanoseconds = (time.time() * int(1e9))
        else:
            raise TypeError("Unparsable input type {}".format(tm.__class__))

    def _pandas_string(self, largest_unit=None):
        str_rep = ''
        ns = float(self._nanoseconds)

        for span in [
            (Time.from_years,        'A'),
            (Time.from_months,       'M'),
            (Time.from_days,         'D'),
            (Time.from_hours,        'H'),
            (Time.from_minutes,      'T'),
            (Time.from_seconds,      'S'),
            (Time.from_milliseconds, 'L'),
            (Time.from_microseconds, 'U'),
            (Time.from_nanoseconds,  'N'),
        ]:
            if largest_unit:
                if largest_unit in PANDAS_UNITS:
                    if PANDAS_UNITS.index(span[1]) < PANDAS_UNITS.index(largest_unit):
                        continue

            span_ns = span[0](1)
            value = ns / span_ns

            if value >= 1.0:
                str_rep += '{}{}'.format(int(value), span[1])
                ns -= int(value) * span_ns

        return str_rep

    @classmethod
    def from_pandas_string(cls, pandas_tm, relative_from=None):
        relative = False
        pandas_tm = RX_SPACE.sub('', pandas_tm)
        pandas_tm = pandas_tm.upper()

        if pandas_tm.startswith('-'):
            relative = True
            pandas_tm = pandas_tm[1:]

        absolute_time = Time(0)

        # iterate through all pattern matches,
        # call the correct nanosecond function for the matched token
        for value, unit in RX_PANDAS_TIMESTR.findall(pandas_tm):
            value = int(value)
            attr = PANDAS_TO_ATTR.get(unit)

            if not attr or not hasattr(absolute_time, attr):
                raise ValueError("Unrecognized unit '{}'".format(unit))

            plus_ns = getattr(absolute_time, attr)(value)
            absolute_time._nanoseconds += plus_ns

        if relative:
            return Time() - absolute_time
        else:
            return absolute_time

    def _parse(self, dt):
        # timedeltas are converted to absolute time since epoch
        if isinstance(dt, datetime.timedelta):
            dt = (datetime.datetime(1970, 1, 1) + dt)

        if isinstance(dt, Time):
            self._nanoseconds = dt._nanoseconds

        elif isinstance(dt, datetime.datetime):
            # figure out cool timezone stuff
            if dt.tzinfo is not None:
                dt = dt.astimezone(tz.gettz('UTC'))
                epoch_dt = datetime.datetime(1970, 1, 1, tzinfo=tz.gettz('UTC'))
            else:
                epoch_dt = datetime.datetime(1970, 1, 1)

            # get epoch seconds
            epoch = (dt - epoch_dt).total_seconds()

            # epoch nanoseconds is epoch + ns (derived from microseconds in dt)
            self._nanoseconds = int(
                Time.from_seconds(epoch)
            ) + int(
                Time.from_microseconds(dt.microsecond)
            )

        elif isinstance(dt, datetime.date):
            self._nanoseconds = long(Time('{}T00:00:00Z'.format(dt.isoformat())))

        else:
            raise TypeError("Unparsable input type {}".format(dt.__class__))

        self._nanoseconds = int(self._nanoseconds)

    def __int__(self):
        return int(self._nanoseconds)

    def __long__(self):
        return long(self._nanoseconds)

    def __add__(self, other):
        if isinstance(other, Time):
            return Time(self._nanoseconds + other._nanoseconds)
        elif isinstance(other, (int, float, long)):
            return Time(self._nanoseconds + other)
        elif isinstance(other, six.string_types + (datetime.datetime, datetime.timedelta)):
            return Time(self._nanoseconds + Time(other)._nanoseconds)
        else:
            return TypeError("'+' operator not supported for type {}".format(
                type(other)
            ))

    def __sub__(self, other):
        if isinstance(other, Time):
            return Time(self._nanoseconds - other._nanoseconds)
        elif isinstance(other, (int, float, long)):
            return Time(self._nanoseconds - other)
        elif isinstance(other, six.string_types + (datetime.datetime, datetime.timedelta)):
            return Time(self._nanoseconds - Time(other)._nanoseconds)
        else:
            return TypeError("'-' operator not supported for type {}".format(
                type(other)
            ))

    def __str__(self):
        return self.isoformat()

    def __repr__(self):
        return self.isoformat()

    def total_seconds(self):
        return int(int(self) / int(1e9))

    def isoformat(self):
        return self.as_datetime().isoformat().rstrip('+00:00')

    @property
    def freq(self):
        return self._pandas_string()

    def convert_to(self, unit):
        return self._pandas_string(largest_unit=unit)

    def as_datetime(self):
        epoch = int(self._nanoseconds / long(1e9))
        ns = float(self._nanoseconds - (epoch * int(1e9)))

        result = datetime.datetime.utcfromtimestamp(
            epoch
        ) + datetime.timedelta(microseconds=int(ns / int(1e3)))

        return pytz.utc.localize(result)

    def as_microseconds(self):
        return Time.to_microseconds(self._nanoseconds)

    def as_milliseconds(self):
        return Time.to_milliseconds(self._nanoseconds)

    def as_seconds(self):
        return Time.to_seconds(self._nanoseconds)

    def as_minutes(self):
        return Time.to_minutes(self._nanoseconds)

    def as_hours(self):
        return Time.to_hours(self._nanoseconds)

    def as_days(self):
        return Time.to_days(self._nanoseconds)

    def as_months(self):
        return Time.to_months(self._nanoseconds)

    def as_years(self):
        return Time.to_years(self._nanoseconds)

    @classmethod
    def from_nanoseconds(cls, val):
        return long(val)

    @classmethod
    def from_microseconds(cls, val):
        return long(val) * long(1e3)

    @classmethod
    def from_milliseconds(cls, val):
        return long(val) * long(1e6)

    @classmethod
    def from_seconds(cls, val):
        return long(val) * long(1e9)

    @classmethod
    def from_minutes(cls, val):
        return long(val * 60 * cls.from_seconds(1))

    @classmethod
    def from_hours(cls, val):
        return long(val * 60 * cls.from_minutes(1))

    @classmethod
    def from_days(cls, val):
        return long(val * 24 * cls.from_hours(1))

    @classmethod
    def from_months(cls, val):
        return long(val * 30 * cls.from_days(1))

    @classmethod
    def from_years(cls, val):
        return long(val * 365 * cls.from_days(1))

    @classmethod
    def to_microseconds(cls, nanoseconds):
        return long(nanoseconds) / 1e3

    @classmethod
    def to_milliseconds(cls, nanoseconds):
        return long(nanoseconds) / 1e6

    @classmethod
    def to_seconds(cls, nanoseconds):
        return long(nanoseconds) / 1e9

    @classmethod
    def to_minutes(cls, nanoseconds):
        return cls.to_seconds(nanoseconds) / 60.0

    @classmethod
    def to_hours(cls, nanoseconds):
        return cls.to_minutes(nanoseconds) / 60.0

    @classmethod
    def to_days(cls, nanoseconds):
        return cls.to_hours(nanoseconds) / 24.0

    @classmethod
    def to_months(cls, nanoseconds):
        return cls.to_days(nanoseconds) / 30.0

    @classmethod
    def to_years(cls, nanoseconds):
        return cls.to_days(nanoseconds) / 365.0
