#!/usr/bin/env python3

"""Encode input using caesar chiffre.

Usage:
  caesar [options]
  caesar -h | --help
  caesar --version

Options:
  -h, --help             Print this message and exit.
  -o, --offset=<offset>  Only rotate by this offset. The default is to print all 26 possible rotations of the input.
  --version              Print version info and exit.
"""

import sys

from docopt import docopt
import string
import syncbin

__version__ = syncbin.__version__

def caesar(s, offset=13):
    """
    Returns the input string s, caesar-encoded with the given offset. Based on http://rosettacode.org/wiki/Rot-13#Python
    """
    return s.translate(str.maketrans(string.ascii_uppercase + string.ascii_lowercase, string.ascii_uppercase[offset:] + string.ascii_uppercase[:offset] + string.ascii_lowercase[offset:] + string.ascii_lowercase[:offset]))

if __name__ == '__main__':
    arguments = docopt(__doc__, version='caesar from fenhl/syncbin ' + __version__)
    if arguments['--offset']:
        offset = int(arguments['--offset'])
    else:
        offset = None
    for line in sys.stdin:
        if offset is None:
            for o in range(26):
                print(caesar(line, o), end='', flush=True)
        else:
            print(caesar(line, offset), end='', flush=True)
