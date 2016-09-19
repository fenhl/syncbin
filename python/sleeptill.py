#!/usr/bin/env python3

"""Sleep until the specified datetime. If the datetime is in the past, this will exit immediately.

Usage:
  sleeptill [options] <date> <time>
  sleeptill [options] <time>
  sleeptill -h | --help
  sleeptill --version

Options:
  -h, --help     Print this message and exit.
  -v, --verbose  Show an info line while sleeping (requires fancyio).
  --version      Print version info and exit.
"""

import datetime
import docopt
import syncbin
import time

__version__ = syncbin.__version__

def sleep_until(end_date):
    """Block until a specified datetime."""
    if end_date <= datetime.datetime.utcnow():
        return
    time.sleep((end_date - datetime.datetime.utcnow()).total_seconds())

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
    if arguments['<date>']:
        end_date = datetime.datetime.strptime(arguments['<date>'] + ' ' + arguments['<time>'], '%Y-%m-%d %H:%M:%S')
    else:
        hours, minutes, seconds = (int(time_unit) for time_unit in arguments['<time>'].split(':'))
        end_date = datetime.datetime.combine(datetime.date.today(), datetime.time(hours, minutes, seconds))
        if end_date < datetime.datetime.utcnow():
            end_date = datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=1), datetime.time(hours, minutes, seconds))
    if arguments['--verbose']:
        verbose_sleep_until(end_date)
    else:
        sleep_until(end_date)
