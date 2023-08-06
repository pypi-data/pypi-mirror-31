#!/usr/bin/env python
# coding: utf-8

# Copyright 2018, Nigel Small & Neo4j
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


""" This module contains the fundamental types used for temporal accounting as well as
a number of utility functions.
"""

from __future__ import division

from neotime.arithmetic import nano_add, nano_sub, nano_mul, nano_div, nano_mod, symmetric_divmod, round_half_to_even, \
    nano_divmod
from neotime.clock import MIN_INT64, MAX_INT64, clock


__version__ = "1.0.0b1"


MIN_YEAR = 1
MAX_YEAR = 9999


class Duration(tuple):
    """ A :class:`.Duration` object...

    i64:i64:i64:i32
    """

    min = None
    max = None

    def __new__(cls, years=0, months=0, weeks=0, days=0, hours=0, minutes=0, seconds=0,
                subseconds=0, milliseconds=0, microseconds=0, nanoseconds=0):
        mo = int(12 * years + months)
        if mo < MIN_INT64 or mo > MAX_INT64:
            raise ValueError("Month out of range")
        d = int(7 * weeks + days)
        if d < MIN_INT64 or d > MAX_INT64:
            raise ValueError("Day out of range")
        s = (int(3600000000000 * hours) +
             int(60000000000 * minutes) +
             int(1000000000 * seconds) +
             int(1000000000 * subseconds) +
             int(1000000 * milliseconds) +
             int(1000 * microseconds) +
             int(nanoseconds))
        s, ss = symmetric_divmod(s, 1000000000)
        if s < MIN_INT64 or s > MAX_INT64:
            raise ValueError("Seconds out of range")
        return tuple.__new__(cls, (mo, d, s, ss / 1000000000))

    def __bool__(self):
        return any(map(bool, self))

    __nonzero__ = __bool__

    def __add__(self, other):
        if not isinstance(other, Duration):
            return NotImplemented
        return Duration(months=self[0] + int(other[0]), days=self[1] + int(other[1]),
                        seconds=self[2] + int(other[2]), subseconds=nano_add(self[3], other[3]))

    def __sub__(self, other):
        if not isinstance(other, Duration):
            return NotImplemented
        return Duration(months=self[0] - int(other[0]), days=self[1] - int(other[1]),
                        seconds=self[2] - int(other[2]), subseconds=nano_sub(self[3], other[3]))

    def __mul__(self, other):
        if not isinstance(other, (int, float)):
            return NotImplemented
        return Duration(months=self[0] * other, days=self[1] * other,
                        seconds=self[2] * other, subseconds=nano_mul(self[3], other))

    def __floordiv__(self, other):
        if not isinstance(other, int):
            return NotImplemented
        return Duration(months=int(self[0] // other), days=int(self[1] // other),
                        seconds=int(nano_add(self[2], self[3]) // other), subseconds=0)

    def __mod__(self, other):
        if not isinstance(other, int):
            return NotImplemented
        seconds, subseconds = symmetric_divmod(nano_add(self[2], self[3]) % other, 1)
        return Duration(months=round_half_to_even(self[0] % other), days=round_half_to_even(self[1] % other),
                        seconds=seconds, subseconds=subseconds)

    def __divmod__(self, other):
        if not isinstance(other, int):
            return NotImplemented
        return self.__floordiv__(other), self.__mod__(other)

    def __truediv__(self, other):
        if not isinstance(other, (int, float)):
            return NotImplemented
        return Duration(months=round_half_to_even(float(self[0]) / other), days=round_half_to_even(float(self[1]) / other),
                        seconds=float(self[2]) / other, subseconds=nano_div(self[3], other))

    __div__ = __truediv__

    def __pos__(self):
        return self

    def __neg__(self):
        return Duration(months=-self[0], days=-self[1], seconds=-self[2], subseconds=-self[3])

    def __abs__(self):
        return Duration(months=abs(self[0]), days=abs(self[1]), seconds=abs(self[2]), subseconds=abs(self[3]))

    def __repr__(self):
        return "Duration(months=%r, days=%r, seconds=%r, subseconds=%r)" % self

    def __str__(self):
        terms = []
        if self[0]:
            terms.append("%+dmo" % self[0])
        if self[1]:
            terms.append("%+dd" % self[1])
        if self[2] or self[3]:
            s = ("%d" if self[2] == 0 else "%+d") % self[2]
            s += ("%.9f" % abs(self[3])).strip("0")
            if s.endswith("."):
                s += "0"
            terms.append("%ss" % s)
        return " ".join(terms)

    def iso_format(self):
        """

        :return:
        """
        years, months, days = self.years_months_days
        hours, minutes, seconds = self.hours_minutes_seconds
        return "P%04d-%02d-%02dT%02d:%02d:%012.9f" % (years, months, days, hours, minutes, seconds)

    @property
    def months(self):
        """

        :return:
        """
        return self[0]

    @property
    def days(self):
        """

        :return:
        """
        return self[1]

    @property
    def seconds(self):
        """

        :return:
        """
        return self[2]

    @property
    def subseconds(self):
        """

        :return:
        """
        return self[3]

    @property
    def years_months_days(self):
        """

        :return:
        """
        years, months = symmetric_divmod(self[0], 12)
        return years, months, self[1]

    @property
    def hours_minutes_seconds(self):
        """ A 3-tuple of (hours, minutes, seconds).
        """
        minutes, seconds = symmetric_divmod(self[2], 60)
        hours, minutes = symmetric_divmod(minutes, 60)
        return hours, minutes, float(seconds) + self[3]


Duration.min = Duration(months=MIN_INT64, days=MIN_INT64, seconds=MIN_INT64, subseconds=-0.999999999)
Duration.max = Duration(months=MAX_INT64, days=MAX_INT64, seconds=MAX_INT64, subseconds=+0.999999999)


class Date(object):

    min = None
    max = None
    resolution = None

    __ordinal = 0
    __year = 0
    __month = 0
    __day = 0

    __never = None

    @classmethod
    def __normalize_year(cls, year):
        if MIN_YEAR <= year <= MAX_YEAR:
            return int(year)
        raise ValueError("Year out of range (%d..%d)" % (MIN_YEAR, MAX_YEAR))

    @classmethod
    def __normalize_month(cls, year, month):
        year = cls.__normalize_year(year)
        if 1 <= month <= 12:
            return year, int(month)
        raise ValueError("Month out of range (1..12)")

    @classmethod
    def __normalize_day(cls, year, month, day):
        """ Coerce the day of the month to an internal value that may or
        may not match the "public" value.

        With the exception of the last three days of every month, all
        days are stored as-is. The last three days are instead stored
        as -1 (the last), -2 (first from last) and -3 (second from last).

        Therefore, for a 28-day month, the last week is as follows:

            Day   | 22 23 24 25 26 27 28
            Value | 22 23 24 25 -3 -2 -1

        For a 29-day month, the last week is as follows:

            Day   | 23 24 25 26 27 28 29
            Value | 23 24 25 26 -3 -2 -1

        For a 30-day month, the last week is as follows:

            Day   | 24 25 26 27 28 29 30
            Value | 24 25 26 27 -3 -2 -1

        For a 31-day month, the last week is as follows:

            Day   | 25 26 27 28 29 30 31
            Value | 25 26 27 28 -3 -2 -1

        This slightly unintuitive system makes some temporal arithmetic
        produce a more desirable outcome.

        :param year:
        :param month:
        :param day:
        :return:
        """
        year, month = cls.__normalize_month(year, month)
        days_in_month = cls.days_in_month(year, month)
        if day in (days_in_month, -1):
            return year, month, -1
        if day in (days_in_month - 1, -2):
            return year, month, -2
        if day in (days_in_month - 2, -3):
            return year, month, -3
        if 1 <= day <= days_in_month - 3:
            return year, month, int(day)
        # TODO improve this error message
        raise ValueError("Day %d out of range (1..%d, -1, -2 ,-3)" % (day, days_in_month))

    @classmethod
    def is_leap_year(cls, year):
        year = cls.__normalize_year(year)
        if year % 4 != 0:
            return False
        if year % 100 != 0:
            return True
        return year % 400 == 0

    @classmethod
    def days_in_year(cls, year):
        return 366 if cls.is_leap_year(year) else 365

    @classmethod
    def days_in_month(cls, year, month):
        year, month = cls.__normalize_month(year, month)
        if month in (9, 4, 6, 11):
            return 30
        elif month != 2:
            return 31
        else:
            return 29 if cls.is_leap_year(year) else 28

    @classmethod
    def from_ordinal(cls, ordinal):
        """ Return the :class:`.Date` that corresponds to the proleptic
        Gregorian ordinal, where ``0001-01-01`` has ordinal 1 and
        ``9999-12-31`` has ordinal 3,652,059. Values outside of this
        range trigger a :exc:`ValueError`. The corresponding instance
        method for the reverse date-to-ordinal transformation is
        :meth:`.to_ordinal`.
        """
        if ordinal == 0:
            return cls.__get_never()
        day = int(ordinal)
        if day < 1 or day > 3652059:
            # Note: this requires a maximum of 22 bits for storage
            # Could be transferred in 3 bytes.
            raise ValueError("Ordinal out of range (1..3652059)")
        year = 1
        month = 1
        days_in_year = cls.days_in_year(year)
        while day > days_in_year:
            day -= days_in_year
            year += 1
            days_in_year = cls.days_in_year(year)
        days_in_month = cls.days_in_month(year, month)
        while day > days_in_month:
            day -= days_in_month
            month += 1
            days_in_month = cls.days_in_month(year, month)
        year, month, day = cls.__normalize_day(year, month, day)
        return cls.__new(ordinal, year, month, day)

    @classmethod
    def __new(cls, ordinal, year, month, day):
        instance = object.__new__(cls)
        instance.__ordinal = int(ordinal)
        instance.__year = int(year)
        instance.__month = int(month)
        instance.__day = int(day)
        return instance

    @classmethod
    def __get_never(cls):
        if cls.__never is None:
            cls.__never = object.__new__(cls)
        return cls.__never

    @classmethod
    def __calc_ordinal(cls, year, month, day):
        if day >= 1:
            ordinal = int(day)
        else:
            ordinal = cls.days_in_month(year, month) + int(day) + 1
        for m in range(1, month):
            ordinal += cls.days_in_month(year, m)
        for y in range(1, year):
            ordinal += cls.days_in_year(y)
        return ordinal

    def __new__(cls, year, month, day):
        if year == month == day == 0:
            return cls.__get_never()
        year, month, day = cls.__normalize_day(year, month, day)
        ordinal = cls.__calc_ordinal(year, month, day)
        return cls.__new(ordinal, year, month, day)

    def __eq__(self, other):
        if isinstance(other, Date):
            return self.ordinal == other.ordinal
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.ordinal)

    def __int__(self):
        return int(self.ordinal)

    def __increment_months(self, months):
        years, months = symmetric_divmod(months, 12)
        year = self.__year + years
        month = self.__month + months
        if month > 12:
            year += 1
            month -= 12
        if month < 1:
            year -= 1
            month -= 12
        self.__year = year
        self.__month = month

    def __increment_days(self, days):
        assert 1 <= self.__day <= 28 or -28 <= self.__day <= -1
        if self.__day >= 1:
            new_days = self.__day + days
            if 1 <= new_days <= 27:
                self.__day = new_days
                return
        new_date = Date.from_ordinal(self.__ordinal + days)
        self.__year, self.__month, self.__day = new_date.__year, new_date.__month, new_date.__day

    def __add__(self, other):
        if isinstance(other, (int, float)):
            if other == 0:
                return self
            new_date = self.replace()
            Date.__increment_days(new_date, other)
            new_date.__ordinal = self.__calc_ordinal(new_date.year, new_date.month, new_date.day)
            return new_date
        if isinstance(other, Duration):
            if other.seconds or other.subseconds:
                raise ValueError("Cannot add a Duration with seconds or subseconds to a Date")
            if other.months == other.days == 0:
                return self
            new_date = self.replace()
            # Add days before months as the former sometimes
            # requires the current ordinal to be correct.
            if other.days:
                Date.__increment_days(new_date, other.days)
            if other.months:
                Date.__increment_months(new_date, other.months)
            new_date.__ordinal = self.__calc_ordinal(new_date.year, new_date.month, new_date.day)
            return new_date
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Date):
            return Duration(days=(self.ordinal - other.ordinal))
        try:
            return self.__add__(-other)
        except TypeError:
            return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Date):
            return self.ordinal < other.ordinal
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, Date):
            return self.ordinal > other.ordinal
        return NotImplemented

    def __repr__(self):
        if self.__ordinal == 0:
            return "Never"
        return "Date(%r, %r, %r)" % self.year_month_day

    def __str__(self):
        if self.__ordinal == 0:
            return "0000-00-00"
        return "%04d-%02d-%02d" % self.year_month_day

    @property
    def ordinal(self):
        """ Return the current value as an ordinal.
        """
        return self.__ordinal

    @property
    def year(self):
        return self.__year

    @property
    def month(self):
        return self.__month

    @property
    def day(self):
        if self.__day == 0:
            return 0
        if self.__day >= 1:
            return self.__day
        return self.days_in_month(self.__year, self.__month) + self.__day + 1

    @property
    def year_month_day(self):
        return self.year, self.month, self.day

    @property
    def year_week_day(self):
        ordinal = self.__ordinal
        year = self.__year

        def day_of_week(o):
            return ((o - 1) % 7) + 1

        def iso_week_1(y):
            j4 = Date(y, 1, 4)
            return j4 + Duration(days=(1 - day_of_week(j4.ordinal)))

        if ordinal >= Date(year, 12, 29).ordinal:
            week1 = iso_week_1(year + 1)
            if ordinal < week1.ordinal:
                week1 = iso_week_1(year)
            else:
                year += 1
        else:
            week1 = iso_week_1(year)
            if ordinal < week1.ordinal:
                year -= 1
                week1 = iso_week_1(year)
        return year, ((ordinal - week1.ordinal) / 7 + 1), day_of_week(ordinal)

    @property
    def year_day(self):
        return self.__year, self.ordinal - Date(self.__year, 1, 1).ordinal + 1

    def replace(self, year=0, month=0, day=0):
        """ Return a :class:`.Date` with one or more components replaced
        with new values.
        """
        return Date(year or self.__year, month or self.__month, day or self.__day)

    @classmethod
    def today_utc(cls):
        t = clock.read_utc()
        return Date.from_ordinal(t.seconds // 86400 + 719163)


Date.min = Date.from_ordinal(1)
Date.max = Date.from_ordinal(3652059)
Date.resolution = Duration(days=1)

Never = Date(0, 0, 0)


class Time(object):
    """ Time of day.
    """

    min = None
    max = None
    resolution = None

    __ticks = 0
    __hour = 0
    __minute = 0
    __second = 0

    __midnight = None

    @classmethod
    def check_ticks(cls, ticks):
        if ticks < 0 or ticks >= 86400:
            raise ValueError("Ticks out of range (0..86400)")

    @classmethod
    def __normalize_hour(cls, hour):
        if 0 <= hour < 24:
            return int(hour)
        raise ValueError("Hour out of range (0..23)")

    @classmethod
    def __normalize_minute(cls, hour, minute):
        hour = cls.__normalize_hour(hour)
        if 0 <= minute < 60:
            return hour, int(minute)
        raise ValueError("Minute out of range (0..59)")

    @classmethod
    def __normalize_second(cls, hour, minute, second):
        hour, minute = cls.__normalize_minute(hour, minute)
        if 0 <= second < 60:
            return hour, minute, float(second)
        raise ValueError("Second out of range (0..<60)")

    @classmethod
    def from_ticks(cls, ticks):
        if ticks == 0:
            return cls.__get_midnight()
        if 0 <= ticks < 86400:
            minute, second = nano_divmod(ticks, 60)
            hour, minute = divmod(minute, 60)
            return cls.__new(ticks, hour, minute, second)
        raise ValueError("Ticks out of range (0..86400)")

    @classmethod
    def __new(cls, ticks, hour, minute, second):
        instance = object.__new__(cls)
        instance.__ticks = float(ticks)
        instance.__hour = int(hour)
        instance.__minute = int(minute)
        instance.__second = float(second)
        return instance

    @classmethod
    def __get_midnight(cls):
        if cls.__midnight is None:
            cls.__midnight = object.__new__(cls)
        return cls.__midnight

    def __new__(cls, hour, minute, second):
        if hour == minute == second == 0:
            return cls.__get_midnight()
        hour, minute, second = cls.__normalize_second(hour, minute, second)
        ticks = 3600 * hour + 60 * minute + second
        return cls.__new(ticks, hour, minute, second)

    def __repr__(self):
        return "Time(%r, %r, %r)" % self.hour_minute_second

    @property
    def ticks(self):
        return self.__ticks

    @property
    def hour(self):
        return self.__hour

    @property
    def minute(self):
        return self.__minute

    @property
    def second(self):
        return self.__second

    @property
    def hour_minute_second(self):
        return self.__hour, self.__minute, self.__second

    def replace(self, hour=0, minute=0, second=0.0):
        """ Return a :class:`.Time` with one or more components replaced
        with new values.
        """
        return Time(hour or self.__hour, minute or self.__minute, second or self.__second)

    @classmethod
    def now_utc(cls):
        t = clock.read_utc()
        nanoseconds = int(1000000000 * (t.seconds % 86400) + t.nanoseconds)
        return Time.from_ticks(nanoseconds / 1000000000)


Midnight = Time(0, 0, 0)
