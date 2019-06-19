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

import pathlib
import sys

sys.path += ['/opt/py', str(pathlib.Path.home() / 'py')]

try:
    import contextlib
    import datetime
    import docopt
    import pytz
    import syncbin
    import time
    import timespec
    import tzlocal
except ImportError:
    if '--relative' in sys.argv:
        import subprocess

        sys.exit(subprocess.call(['sleep'] + [arg for arg in sys.argv[1:] if arg != '--relative']))
    else:
        raise

__version__ = syncbin.__version__

def sleep_until(end_date):
    """Block until a specified datetime."""
    if end_date <= datetime.datetime.now(datetime.timezone.utc):
        return
    time.sleep((end_date - datetime.datetime.now(datetime.timezone.utc)).total_seconds())

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
        end_date = pytz.utc.localize(datetime.datetime.utcnow())
        assert timespec.is_aware(end_date)
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
            assert timespec.is_aware(end_date)
    else:
        end_date = timespec.parse(arguments['<timespec>'], tz=tz)
    if arguments['--verbose']:
        verbose_sleep_until(end_date)
    else:
        sleep_until(end_date)
