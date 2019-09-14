#!/usr/bin/env python3

"""Create a new JSON file and open it with `jpy`

Usage:
  jinit [options] <file>
  jinit -h | --help

Options:
  -a, --array           Initialize with an empty array instead of an object.
  -h, --help            Print this message and exit.
  -n, --noninteractive  Don't open `jpy`, just create the file.
  --version             Print version info and exit.
"""

import sys

if __name__ != '__main__':
    sys.exit('This module is not for importing!')

import docopt
import pathlib
import subprocess
try:
    import syncbin
    __version__ = syncbin.__version__
except:
    __version__ = '0.0'

arguments = docopt.docopt(__doc__, version='jinit from fenhl/syncbin ' + __version__)

path = pathlib.Path(arguments['<file>'])

if path.exists():
    sys.exit('[!!!!] file exists')

if not path.parent.exists():
    path.parent.mkdir(parents=True)

with path.open('w') as f:
    print('[]' if arguments['--array'] else '{}', file=f)

if not arguments['--noninteractive']:
    sys.exit(subprocess.call(['jpy', arguments['<file>']]))
