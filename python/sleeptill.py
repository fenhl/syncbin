#!/usr/bin/env python3

"""Sleep until the specified datetime. If the datetime is in the past, this will exit immediately.

Usage:
  sleeptill [options] <timespec>...
  sleeptill [options] --relative <interval>...
  sleeptill -h | --help
  sleeptill --version

Options:
  -h, --help                 Print this message and exit.
  -v, --verbose              Show an info line while sleeping (requires fancyio).
  -z, --timezone=<timezone>  Use the specified timezone instead of the system timezone.
  --relative                 Sleep for the sum of the specified intervals. Default unit is seconds, but s/m/h/d can be used to specify seconds/minutes/hours/days.
  --version                  Print version info and exit.
"""

import sys

import contextlib
import datetime
import docopt
import pytz
import syncbin
import time
import tzlocal

__version__ = syncbin.__version__

def date_range(start, end):
    date = start
    while date < end:
        yield date
        date += datetime.timedelta(days=1)

def equals_predicate(value):
    return lambda v: v == value

def is_aware(datetime_or_time):
    if isinstance(datetime_or_time, datetime.datetime):
        return datetime_or_time.tzinfo is not None and datetime_or_time.tzinfo.utcoffset(datetime_or_time) is not None
    elif isinstance(datetime_or_time, datetime.time):
        return datetime_or_time.tzinfo is not None and datetime_or_time.tzinfo.utcoffset(None) is not None
    else:
        raise TypeError('Can only test datetime or time objects for awareness')

def parse_iso_date(date_str):
    parts = date_str.split('-')
    if len(parts) != 3:
        raise ValueError('Failed to parse date from {!r} (format should be YYYY-MM-DD)'.format(date_str))
    return datetime.date(*map(int, parts))

def predicate_set(predicates, values):
    result = set(resolve_predicates(predicates, values))
    if len(result) == 0:
        sys.exit('[!!!!] no matching datetime found')
    return result

def resolve_predicates(predicates, values):
    for val in values:
        if all(predicate(val) for predicate in predicates):
            yield val

def sleep_until(end_date):
    """Block until a specified datetime."""
    if end_date <= datetime.datetime.now(datetime.timezone.utc):
        return
    time.sleep((end_date - datetime.datetime.now(datetime.timezone.utc)).total_seconds())

def time_range(tz=datetime.timezone.utc):
    for hour in range(24):
        for minute in range(60):
            for second in range(60):
                yield datetime.time(hour, minute, second, tzinfo=tz)

def verbose_sleep_until(end_date, io=None):
    import fancyio

    def _verbose_sleep_inner(inner_io):
        sleep_line = fancyio.SleepLine(inner_io, end=end_date)
        sleep_line.join()

    if io is None:
        with fancyio.IO() as new_io:
            _verbose_sleep_inner(inner_io=new_io)
    else:
        _verbose_sleep_inner(inner_io=io)

if __name__ == '__main__':
    arguments = docopt.docopt(__doc__, version='sleeptill from fenhl/syncbin ' + __version__)
    if arguments['--timezone']:
        tz = pytz.timezone(arguments['--timezone'])
    else:
        tz = tzlocal.get_localzone()
    if arguments['--relative']:
        end_date = datetime.datetime.now(tz)
        assert is_aware(end_date)
        for interval_str in arguments['<interval>']:
            if interval_str.endswith('s'):
                end_date += datetime.timedelta(seconds=float(interval_str[:-1]))
            elif interval_str.endswith('m'):
                end_date += datetime.timedelta(minutes=float(interval_str[:-1]))
            elif interval_str.endswith('h'):
                end_date += datetime.timedelta(hours=float(interval_str[:-1]))
            elif interval_str.endswith('d'):
                end_date += datetime.timedelta(days=float(interval_str[:-1]))
            else:
                end_date += datetime.timedelta(seconds=float(interval_str))
            assert is_aware(end_date)
    else:
        now = datetime.datetime.now(tz)
        year_predicates = []
        month_predicates = []
        day_predicates = []
        hour_predicates = []
        minute_predicates = []
        second_predicates = []
        for predicate_str in arguments['<timespec>']:
            with contextlib.suppress(ValueError):
                end_date = parse_iso_date(predicate_str)
                if end_date < now.date():
                    sys.exit('[!!!!] specified date is in the past')
                year_predicates.append(lambda y: y == end_date.year)
                month_predicates.append(lambda m: m == end_date.month)
                day_predicates.append(lambda d: d == end_date.day)
                continue
            if ':' in predicate_str:
                if len(predicate_str.split(':')) == 3:
                    hours, minutes, seconds = (int(time_unit) for time_unit in predicate_str.split(':'))
                    hour_predicates.append(equals_predicate(hours))
                    minute_predicates.append(equals_predicate(minutes))
                    second_predicates.append(equals_predicate(seconds))
                else:
                    hours, minutes = (int(time_unit) for time_unit in predicate_str.split(':'))
                    hour_predicates.append(equals_predicate(hours))
                    minute_predicates.append(equals_predicate(minutes))
                continue
            sys.exit('[!!!!] unknown timespec')
        years = predicate_set(year_predicates, range(now.year, now.year + 100))
        months = predicate_set(month_predicates, range(1, 13))
        days = predicate_set(day_predicates, range(1, 32))
        date_predicates = {
            lambda date: date.year in years,
            lambda date: date.month in months,
            lambda date: date.day in days
        }
        dates = predicate_set(date_predicates, date_range(now.date(), now.date().replace(year=now.year + 100)))
        hours = predicate_set(hour_predicates, range(24))
        minutes = predicate_set(minute_predicates, range(60))
        seconds = predicate_set(second_predicates, range(60))
        time_predicates = {
            lambda time: time.hour in hours,
            lambda time: time.minute in minutes,
            lambda time: time.second in seconds
        }
        times = predicate_set(time_predicates, time_range(tz))
        datetime_predicates = {
            lambda date_time: date_time.date() in dates,
            lambda date_time: date_time.timetz() in times,
            lambda date_time: date_time > now
        }
        end_date = min(resolve_predicates(datetime_predicates, (datetime.datetime.combine(date, time) for date in dates for time in times)))
        assert is_aware(end_date)
    if arguments['--verbose']:
        verbose_sleep_until(end_date)
    else:
        sleep_until(end_date)
