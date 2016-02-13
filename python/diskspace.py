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
import re
import subprocess
try:
    import syncbin
    __version__ = syncbin.__version__
except:
    __version__ = '0.0'

def format_space(num_bytes):
    if num_bytes >= 2 ** 50:
        return str(num_bytes // (2 ** 50)) + 'PB'
    if num_bytes >= 2 ** 40:
        return str(num_bytes // (2 ** 40)) + 'TB'
    if num_bytes >= 2 ** 30:
        return str(num_bytes // (2 ** 30)) + 'GB'
    if num_bytes >= 2 ** 20:
        return str(num_bytes // (2 ** 20)) + 'MB'
    if num_bytes >= 2 ** 10:
        return str(num_bytes // (2 ** 20)) + 'KB'
    return str(int(num_bytes))

def parse_space(space_string):
    space_string = str(space_string)
    match = re.match('([0-9.]+)([PTGMKB])', space_string)
    if match:
        amount, unit = match.group(1, 2)
        return int({
            'P': 2 ** 50,
            'T': 2 ** 40,
            'G': 2 ** 30,
            'M': 2 ** 20,
            'K': 2 ** 10,
            'B': 1
        }[unit] * float(amount))
    return int(space_string)

ONE_GIG = 2 ** 30

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
        min_space = 0 if arguments['--min-percent'] else float('inf')
    try:
        output = subprocess.check_output(['df', '-hl', '/'], stderr=subprocess.STDOUT).decode('utf-8')
        total = parse_space(output.splitlines()[1].split()[1])
        available = parse_space(output.splitlines()[1].split()[3])
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
            print('Available disk space:', format_space(available))
            print(str(available), 'bytes')
            print(str(int(100 * available / total)), 'percent')
        elif arguments['--bytes']:
            print(str(available))
        else:
            print('[disk: ' + format_space(available) + ']')
