import datetime as _datetime
from functools import partial, wraps
from typing import Iterator, Tuple, Union

import pytz

from saturn import from_arrow

# No need to import datetime, date, and today if using saturn.
timedelta = _datetime.timedelta
date = _datetime.date
today = _datetime.date.today

DateOrDatetime = Union[_datetime.date, _datetime.datetime]
TimeOrDatetime = Union[_datetime.time, _datetime.datetime]
DateOrTimeOrDatetime = Union[_datetime.date, _datetime.time, _datetime.datetime]


class TzNaiveError(Exception):
    pass

# todo reorder func arguments to be curry-friendly? Needs toolz to support annotations.


def _check_aware_input(func, num_dt_args=1):
    """Force a function that accepts a datetime as first argument to check for
    timezone-awareness.  Raise an error if the input's naive."""
    @wraps(func)
    def inner(*args, **kwargs):
        dts = args[:num_dt_args]
        # Can't use isinstance, since isinstance([datetime object], _datetime.date)
        # returns True.
        for dt in dts:
            if type(dt) != _datetime.date:
                if not dt.tzinfo:
                    raise TzNaiveError("Must use a timezone-aware datetime. Consider saturn.fix_naive().")

        return func(*args, **kwargs)
    return inner


def _check_aware_output(func):
    """Check if a function's output is timezone-aware. Func's first output must
    be the dt; second must be a tz. Used  on functions where the result may, or
    may not be tz-aware already. If already, tz is ignored."""
    @wraps(func)
    def inner(*args, **kwargs):
        dt, tz = func(*args, **kwargs)
        if not dt.tzinfo:  # The time component might have a tzinfo.
            return fix_naive(dt, tz)
        return dt

    return inner


def _check_aware_input_2args(func):
    return _check_aware_input(func, num_dt_args=2)


@_check_aware_output
def datetime(year: int, month: int, day: int, hour: int=0, minute: int=0,
             second: int=0, microsecond: int=0, tzinfo=None, tz: str='UTC') -> _datetime.datetime:
    """Create a datetime instance, with default tzawareness at UTC. A provided
    tzinfo argument overrides a provided tz string."""

    dt = _datetime.datetime(year, month, day, hour, minute, second,
                            microsecond, tzinfo)
    return dt, tz


@_check_aware_output
def time(hour: int, minute: int=0, second: int=0,
         microsecond: int=0, tzinfo=None, tz: str='UTC') -> _datetime.time:
    """Create a time instance, with default tzawareness at UTC."""
    t = _datetime.time(hour, minute, second, microsecond, tzinfo)
    return t, tz


def now() -> _datetime.datetime:
    """Similar to datetime.datetime.utcnow, but tz-aware."""
    # return from_datetime(datetime.datetime.utcnow().replace(tzinfo=pytz.utc))
    return _datetime.datetime.utcnow().replace(tzinfo=pytz.utc)


@_check_aware_output
def combine(date_: _datetime.date, time_: _datetime.time, tz: str='UTC') -> _datetime.datetime:
    """Similar to datetime.datetime.combine, but tz-aware.  The optional
    tz argument won't override a tz included in the time component."""
    return _datetime.datetime.combine(date_, time_), tz


@_check_aware_input
def split(dt: _datetime) -> Tuple[_datetime.date, _datetime.time]:
    """Split a datetime into date and time components.  Useful over calling
    .date() and .time() methods, since that dumps tzinfo for the time component."""
    time_ = time(dt.hour, dt.minute, dt.second, dt.microsecond, dt.tzinfo)
    return dt.date(), time_


def fix_naive(dt: TimeOrDatetime, tz: str='UTC') -> _datetime.datetime:
    """Convert a tz-naive datetime to tz-aware. Default to UTC"""
    return pytz.timezone(tz).localize(dt)


@_check_aware_input
def to_str(dt: DateOrDatetime, str_format: str) -> str:
    """Format a datetime or date as a string."""
    return from_arrow.format_(dt, str_format)


def from_str(dt_str: str, str_format: str, tz: str='UTC') -> \
        Union[_datetime.datetime, _datetime.datetime, _datetime.time]:
    """Format a string to datetime.  Similar to datetime.strptime. The optional
    tz argument won't override a tz included in the string."""
    parsed_dt = from_arrow.parse(dt_str, str_format)

    # Return date, time, or datetime objects as appropriate.
    if not any([parsed_dt.hour, parsed_dt.minute, parsed_dt.second, parsed_dt.microsecond]):
        if parsed_dt.year == 1 and parsed_dt.month == 1 and parsed_dt.day == 1:
            return fix_naive(parsed_dt.time(), tz)
        return parsed_dt.date()

    elif parsed_dt.year == 1 and parsed_dt.month == 1 and parsed_dt.day == 1:
        parsed_dt = parsed_dt.time()

    # We don't use the decorator here, since checking for TZ doesn't apply to Dates.
    if not parsed_dt.tzinfo:  # The time component might have a tzinfo.
        return fix_naive(parsed_dt, tz)


@_check_aware_input
def to_iso(dt: DateOrDatetime) -> str:
    """Return a standard ISO 8601 datetime string.  Similar to datetime's
    .isoformat()"""
    return dt.isoformat()


@_check_aware_output
def from_iso(iso_str: str, tz: str='UTC') -> _datetime.datetime:
    """Convert an ISO 8601 string to a datetime.  The optional
    tz argument won't override a tz included in the string."""
    return from_arrow.parse_iso(iso_str), tz


@_check_aware_input
def to_epoch(dt: DateOrDatetime) -> float:
    return dt.timestamp()


@_check_aware_output
def from_epoch(epoch: float, tz: str='UTC') -> _datetime.datetime:
    return _datetime.datetime.fromtimestamp(epoch), tz


def move_tz(dt: _datetime.datetime, tz: str) -> _datetime.datetime:
    """Change a datetime from one timezone to another."""
    # Datetime provides a ValueError if you use this function on a naive DT, so
    # no need to explicitly raise an error here.
    return dt.astimezone(pytz.timezone(tz))


def _count_timedelta(delta: _datetime.timedelta, step: int, seconds_in_interval: int) -> int:
    """Helper function for iterate.  Finds the number of intervals in the timedelta."""
    return int(delta.total_seconds() / (seconds_in_interval * step))


@_check_aware_input
def add(dt: DateOrDatetime, days: float=0, seconds: float=0, microseconds: float=0,
        milliseconds: float=0, minutes: float=0, hours: float=0, weeks: float=0) -> DateOrDatetime:
    return dt + timedelta(days=days, seconds=seconds, microseconds=microseconds,
                          milliseconds=milliseconds, minutes=minutes, hours=hours,
                          weeks=weeks)


@_check_aware_input
def subtract(dt: DateOrDatetime, days: float=0, seconds: float=0, microseconds: float=0,
             milliseconds: float=0, minutes: float=0, hours: float=0, weeks: float=0) -> DateOrDatetime:
    return dt - timedelta(days=days, seconds=seconds,
                          microseconds=microseconds,
                          milliseconds=milliseconds, minutes=minutes,
                          hours=hours,
                          weeks=weeks)


@_check_aware_input_2args
def range_dt(start: DateOrDatetime, end: DateOrDatetime, step: int=1,
             interval: str='day') -> Iterator[_datetime.datetime]:
    """Iterate over datetimes or dates, similar to builtin range."""
    intervals = partial(_count_timedelta, (end - start), step)

    if interval == 'week':
        for i in range(intervals(3600 * 24 * 7)):
            yield start + _datetime.timedelta(weeks=i) * step

    elif interval == 'day':
        for i in range(intervals(3600 * 24)):
            yield start + _datetime.timedelta(days=i) * step

    elif interval == 'hour':
        for i in range(intervals(3600)):
            yield start + _datetime.timedelta(hours=i) * step

    elif interval == 'minute':
        for i in range(intervals(60)):
            yield start + _datetime.timedelta(minutes=i) * step

    elif interval == 'second':
        for i in range(intervals(1)):
            yield start + _datetime.timedelta(seconds=i) * step

    elif interval == 'millisecond':
        for i in range(intervals(1 / 1000)):
            yield start + _datetime.timedelta(milliseconds=i) * step

    elif interval == 'microsecond':
        for i in range(intervals(1e-6)):
            yield start + _datetime.timedelta(microseconds=i) * step

    else:
        raise AttributeError("Interval must be 'week', 'day', 'hour' 'second', \
            'microsecond' or 'millisecond'.")


def overlaps(start1: DateOrTimeOrDatetime, end1: DateOrTimeOrDatetime,
             start2: DateOrTimeOrDatetime, end2: DateOrTimeOrDatetime) -> bool:
    """Return True if the Two dts overlap False otherwise."""
    return (start1 <= end2 and end1 >= start2) or (start2 <= end1 and end2 >= start1)
