#!/usr/bin/env python3

"""Config and helper tool for Fenhl's syncbin.

Usage:
  syncbin bootstrap [<setup>]
  syncbin hasinet
  syncbin install
  syncbin startup [--ignore-lock]
  syncbin update [<old> <new>]
  syncbin -h | --help
  syncbin --version

Options:
  -h, --help     Print this message and exit.
  --ignore-lock  When used with the `startup' subcommand, ignore the lock that prevents 2 startup scripts from running in parallel.
  --version      Print version info and exit.
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

def bootstrap(setup):
    sys.exit('[!!!!] no such setup: ' + repr(setup)) #TODO

if __name__ == '__main__':
    arguments = docopt(__doc__, version='fenhl/syncbin ' + __version__)
    if arguments['bootstrap']:
        bootstrap(arguments['<setup>'])
    elif arguments['hasinet']:
        sys.exit(subprocess.call(['syncbin-hasinet']))
    elif arguments['install']:
        sys.exit(subprocess.call(['sh', os.path.join(os.environ.get('HUB', '/opt/hub'), 'fenhl', 'syncbin', 'config', 'install.sh')]))
    elif arguments['startup']:
        sys.exit(subprocess.call(['syncbin-startup'] + (['--ignore-lock'] if arguments['--ignore-lock'] else [])))
    elif arguments['update']:
        if arguments['<old>'] is None:
            sys.exit(subprocess.call(['syncbin-update']))
        else:
            sys.exit(subprocess.call(['syncbin-update', arguments['<old>'], arguments['<new>']]))
    else:
        raise NotImplementedError('unknown subcommand')
