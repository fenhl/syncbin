#!/usr/bin/env python3

"""Show available space on main disk

Usage:
  diskspace [options]
  diskspace -h | --help
  diskspace --version

Options:
  -h, --help  Print this message and exit.
  --bytes     Print the raw number of bytes instead of a human-readable format.
  --debug     If an error occurs, print the traceback instead of a generic error message.
  --version   Print version info and exit.
  --zsh       For using in the zsh right prompt, produce no output if more than 1 GB available.
"""

import sys

import re
import subprocess
import syncbin

__version__ = syncbin.__version__

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
    if '-h' in sys.argv or '--help' in sys.argv:
        print(__doc__)
        sys.exit()
    if '--version' in sys.argv:
        print('diskspace from fenhl/syncbin ' + __version__)
        sys.exit()
    try:
        output = subprocess.check_output(['df', '-hl', '/'], stderr=subprocess.STDOUT).decode('utf-8')
        space = parse_space(output.splitlines()[1].split()[3])
    except:
        if '--debug' in sys.argv:
            raise
        else:
            print('[disk: error]')
            sys.exit(1)
    if '--zsh' not in sys.argv or space < ONE_GIG:
        if '--bytes' in sys.argv:
            print(str(space))
        else:
            print('[disk: ' + format_space(space) + ']')
