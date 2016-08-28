#!/usr/bin/env python3

"""Show available space on main disk

Usage:
  diskspace [options]
  diskspace -h | --help
  diskspace --version

Options:
  -V, --verbose                Produce more detailed output. Implies --debug.
  -h, --help                   Print this message and exit.
  -q, --quiet                  Produce no output unless an error occurs during the calculation. Exit status will be 1 if less than --min-percent or --min-space available.
  --bytes                      Print the raw number of bytes instead of a human-readable format.
  --debug                      If an error occurs, print the traceback instead of a generic error message.
  --min-percent=<min_percent>  Produce no output if at least <min_percent>% of disk space is available.
  --min-space=<min_space>      Produce no output if at least <min_space> GB is available.
  --version                    Print version info and exit.
  --zsh                        Defaults for using in the zsh right prompt, equivalent to --min-percent=1 --min-space=1.
"""

import sys

import docopt
import shutil

try:
    import syncbin
    __version__ = syncbin.version()
except:
    __version__ = '0.0'

class Bytes(int):
    def __format__(self, format_spec):
        if format_spec == 'B':
            return str(int(self))
        if format_spec == '':
            return str(self)
        raise ValueError('Invalid format spec {!r}'.format(format_spec))

    def __repr__(self):
        return 'Bytes({!r})'.format(int(self))

    def __str__(self):
        if self >= 2 ** 50:
            return str(int(self) // (2 ** 50)) + 'PB'
        if self >= 2 ** 40:
            return str(int(self) // (2 ** 40)) + 'TB'
        if self >= 2 ** 30:
            return str(int(self) // (2 ** 30)) + 'GB'
        if self >= 2 ** 20:
            return str(int(self) // (2 ** 20)) + 'MB'
        if self >= 2 ** 10:
            return str(int(self) // (2 ** 20)) + 'KB'
        return str(int(self)) + 'B'

ONE_GIG = Bytes(2 ** 30)

if __name__ == '__main__':
    arguments = docopt.docopt(__doc__, version='diskspace from fenhl/syncbin ' + __version__)
    if arguments['--min-percent']:
        min_fraction = int(arguments['--min-percent']) / 100
    elif arguments['--zsh']:
        min_fraction = 0.01
    else:
        min_fraction = 0 if arguments['--min-space'] else float('inf')
    if arguments['--min-space']:
        min_space = int(arguments['--min-space']) * ONE_GIG
    elif arguments['--zsh']:
        min_space = ONE_GIG
    else:
        min_space = Bytes(0) if arguments['--min-percent'] else float('inf')
    try:
        usage = shutil.disk_usage('/')
        total = Bytes(usage.total)
        available = Bytes(usage.free)
    except:
        if arguments['--debug'] or arguments['--verbose']:
            raise
        else:
            print('[disk: error]')
            sys.exit(1)
    if available < min_space or available / total < min_fraction:
        if arguments['--quiet']:
            sys.exit(1)
        elif arguments['--verbose']:
            print('Available disk space: {}'.format(available))
            print('{:B} bytes'.format(available))
            print('{} percent'.format(int(100 * available / total)))
        elif arguments['--bytes']:
            print('{:B}'.format(available))
        else:
            print('[disk: {}]'.format(available))
