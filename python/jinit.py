#!/usr/bin/env python3

"""Create a new JSON file and open it with `jpy`

Usage:
  jinit [options] <file>
  jinit -h | --help

Options:
  -a, --array  Initialize with an empty array instead of an object.
  -h, --help   Print this message and exit.
  --version    Print version info and exit.
"""

import sys

if __name__ != '__main__':
    sys.exit('This module is not for importing!')

import docopt
import os.path
import subprocess
try:
    import syncbin
    __version__ = syncbin.__version__
except:
    __version__ = '0.0'

arguments = docopt.docopt(__doc__, version='jinit from fenhl/syncbin ' + __version__)

if os.path.exists(arguments['<file>']):
    sys.exit('[!!!!] file exists')

with open(arguments['<file>'], 'w') as f:
    print('[]' if arguments['--array'] else '{}', file=f)

sys.exit(subprocess.call(['jpy', arguments['<file>']]))
