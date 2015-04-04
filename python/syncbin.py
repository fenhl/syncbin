#!/usr/bin/env python3

"""Config and helper tool for Fenhl's syncbin.

Usage:
  syncbin bootstrap [<setup>]
  syncbin hasinet
  syncbin install
  syncbin startup [--ignore-lock] [--no-internet-test]
  syncbin update [<old> <new>]
  syncbin -h | --help
  syncbin --version

Options:
  -h, --help          Print this message and exit.
  --ignore-lock       When used with the `startup' subcommand, release and ignore the lock that prevents the startup script from running multiple times at once.
  --no-internet-test  When used with the `startup' subcommand, do not run `syncbin-hasinet' to test for internet connectivity, but run all other startup scripts regardless.
  --version           Print version info and exit.
"""

import sys

from docopt import docopt
import os
import subprocess

try:
    with open(os.path.join(os.environ.get('GITDIR', '/opt/git'), 'github.com', 'fenhl', 'syncbin', 'master', 'version.txt')) as version_file:
        __version__ = version_file.read().strip()
except:
    __version__ = '0.0'

def bootstrap(setup):
    if setup == 'debian-root':
        subprocess.check_call(['apt-get', 'install', 'ntp'])
    else:
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
        sys.exit(subprocess.call(['syncbin-startup'] + (['--ignore-lock'] if arguments['--ignore-lock'] else []) + (['--no-internet-test'] if arguments['--no-internet-test'] else [])))
    elif arguments['update']:
        try:
            with open('/dev/null', 'a') as dev_null:
                subprocess.check_call(['which', 'zsh'], stdout=dev_null)
        except subprocess.CalledProcessError:
            # Zsh missing, use bash
            if arguments['<old>'] is None:
                sys.exit(subprocess.call(['bash', 'syncbin-update']))
            else:
                sys.exit(subprocess.call(['bash', 'syncbin-update', arguments['<old>'], arguments['<new>']]))
        else:
            # use Zsh
            if arguments['<old>'] is None:
                sys.exit(subprocess.call(['syncbin-update']))
            else:
                sys.exit(subprocess.call(['syncbin-update', arguments['<old>'], arguments['<new>']]))
    else:
        raise NotImplementedError('unknown subcommand')
