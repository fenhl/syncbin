#!/usr/bin/env python3

"""Config and helper tool for Fenhl's syncbin.

Usage:
  syncbin bootstrap [<setup>]
  syncbin hasinet
  syncbin install
  syncbin startup [--ignore-lock] [--no-internet-test]
  syncbin update [public | private | hooks] [<old> <new>]
  syncbin -h | --help
  syncbin --version

Options:
  -h, --help          Print this message and exit.
  --ignore-lock       When used with the `startup' subcommand, release and ignore the lock that prevents the startup script from running multiple times at once.
  --no-internet-test  When used with the `startup' subcommand, do not run `syncbin-hasinet' to test for internet connectivity, but run all other startup scripts regardless.
  --version           Print version info and exit.
"""

import sys

try:
    from docopt import docopt
except ImportError:
    print('[ !! ] docopt not installed, defaulting to `syncbin bootstrap python`', file=sys.stderr)
import os
import pathlib
import subprocess

GITDIR = pathlib.Path(os.environ.get('GITDIR', '/opt/git'))

try:
    with (GITDIR / 'github.com' / 'fenhl' / 'syncbin' / 'master' / 'version.txt').open() as version_file:
        __version__ = version_file.read().strip()
except:
    __version__ = '0.0'

def bootstrap(setup):
    if setup == 'debian-root':
        subprocess.check_call(['apt-get', 'install', 'ntp'])
    elif setup == 'python':
        subprocess.check_call(['pip3', 'install', 'blessings'])
        subprocess.check_call(['pip3', 'install', 'docopt'])
    elif setup == 'syncbin-private':
        (GITDIR / 'fenhl.net' / 'syncbin-private').mkdir(parents=True)
        subprocess.check_call(['git', 'clone', 'fenhl@fenhl.net:/opt/git/localhost/syncbin-private/syncbin-private.git', 'master'], cwd=str(GITDIR / 'fenhl.net' / 'sycbin-private'))
    else:
        sys.exit('[!!!!] no such setup: ' + repr(setup)) #TODO

if __name__ == '__main__':
    try:
        arguments = docopt(__doc__, version='fenhl/syncbin ' + __version__)
    except NameError:
        arguments = {
            'bootstrap': True,
            'setup': ['python']
        }
    if arguments['bootstrap']:
        bootstrap(arguments['<setup>'])
    elif arguments['hasinet']:
        sys.exit(subprocess.call(['syncbin-hasinet']))
    elif arguments['install']:
        sys.exit(subprocess.call(['sh', str(GITDIR / 'github.com' / 'fenhl' / 'syncbin' / 'master' / 'config' / 'install.sh')]))
    elif arguments['startup']:
        sys.exit(subprocess.call(['syncbin-startup'] + (['--ignore-lock'] if arguments['--ignore-lock'] else []) + (['--no-internet-test'] if arguments['--no-internet-test'] else [])))
    elif arguments['update']:
        mode = None
        if arguments['public']:
            mode = 'public'
        elif arguments['private']:
            mode = 'private'
        elif arguments['hooks']:
            mode = 'hooks'
        try:
            with open('/dev/null', 'a') as dev_null:
                subprocess.check_call(['which', 'zsh'], stdout=dev_null)
        except subprocess.CalledProcessError:
            # Zsh missing, use bash
            if arguments['<old>'] is None:
                sys.exit(subprocess.call(['bash', 'syncbin-update'] + ([] if mode is None else [mode])))
            else:
                sys.exit(subprocess.call(['bash', 'syncbin-update'] + ([] if mode is None else [mode]) + [arguments['<old>'], arguments['<new>']]))
        else:
            # use Zsh
            if arguments['<old>'] is None:
                sys.exit(subprocess.call(['syncbin-update'] + ([] if mode is None else [mode])))
            else:
                sys.exit(subprocess.call(['syncbin-update'] + ([] if mode is None else [mode]) + [arguments['<old>'], arguments['<new>']]))
    else:
        raise NotImplementedError('unknown subcommand')
