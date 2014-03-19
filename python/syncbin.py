#!/usr/bin/env python3

"""Config and helper tool for Fenhl's syncbin.

Usage:
  syncbin hasinet
  syncbin startup
  syncbin update [<old> <new>]
  syncbin -h | --help
  syncbin --version

Options:
  -h, --help  Print this message and exit.
  --version   Print version info and exit.
"""

import sys

from docopt import docopt
import os
import subprocess

try:
    with open(os.path.join(os.environ.get('HUB', '/opt/hub'), 'fenhl', 'syncbin', 'version.txt')) as version_file:
        __version__ = version_file.read().strip()
except:
    __version__ = '0.0'

if __name__ == '__main__':
    arguments = docopt(__doc__, version='syncbin ' + __version__)
    if arguments['hasinet']:
        sys.exit(subprocess.call(['syncbin-hasinet']))
    elif arguments['startup']:
        sys.exit(subprocess.call(['syncbin-startup']))
    elif arguments['update']:
        if arguments['<old>'] is None:
            sys.exit(subprocess.call(['syncbin-update']))
        else:
            sys.exit(subprocess.call(['syncbin-update', arguments['<old>'], arguments['<new>']]))
    else:
        raise NotImplementedError('unknown subcommand')
