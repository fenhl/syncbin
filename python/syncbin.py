#!/usr/bin/env python3

"""Config and helper tool for Fenhl's syncbin.

Usage:
  syncbin bootstrap <setup>...
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

sys.path.append('/opt/py')

import os
import pathlib
import subprocess

try:
    from docopt import docopt
except ImportError:
    if __name__ == '__main__':
        print('[ !! ] docopt not installed, defaulting to `syncbin bootstrap python`', file=sys.stderr)

BOOTSTRAP_SETUPS = {}
GITDIR = pathlib.Path(os.environ.get('GITDIR', '/opt/git'))

try:
    with (GITDIR / 'github.com' / 'fenhl' / 'syncbin' / 'master' / 'version.txt').open() as version_file:
        __version__ = version_file.read().strip()
except:
    __version__ = '0.0'

def bootstrap_setup(setup_name):
    def inner_wrapper(f):
        BOOTSTRAP_SETUPS[setup_name] = f
        return f
    return inner_wrapper

@bootstrap_setup('debian-root')
def bootstrap_debian_root():
    subprocess.check_call(['apt-get', 'install', 'ntp'])

@bootstrap_setup('gitdir')
def bootstrap_gitdir():
    (GITDIR / 'github.com' / 'fenhl' / 'gitdir').mkdir(parents=True)
    subprocess.check_call(['git', 'clone', 'https://github.com/fenhl/gitdir.git', 'master'], cwd=str(GITDIR / 'github.com' / 'fenhl' / 'gitdir'))
    pathlib.Path('/opt/py/gitdir').symlink_to(GITDIR / 'github.com' / 'fenhl' / 'gitdir' / 'master' / 'gitdir')
    if hasattr(pathlib.Path, 'home'):
        (pathlib.Path.home() / 'bin' / 'gitdir').symlink_to(GITDIR / 'fenhl' / 'gitdir' / 'master' / 'gitdir' / '__main__.py')
    else:
        print('[ ** ] now add a symlink to {} to the PATH'.format(GITDIR / 'fenhl' / 'gitdir' / 'master' / 'gitdir' / '__main__.py'))

@bootstrap_setup('python')
def bootstrap_python():
    subprocess.check_call(['pip3', 'install', 'blessings'])
    subprocess.check_call(['pip3', 'install', 'docopt'])

@bootstrap_setup('sudo')
def bootstrap_sudo():
    print('[ ** ] For passwordless login, insert the following line into the opened document:')
    print('fenhl ALL=(ALL) NOPASSWD: ALL')
    input('[ ?? ] Press return to continue')
    subprocess.check_call(['sudo', 'nano', '/etc/sudoers.d/fenhl'])

@bootstrap_setup('syncbin-private')
def bootstrap_syncbin_private():
    import gitdir.host

    gitdir.host.by_name('fenhl.net').clone('syncbin-private')

def bootstrap(*setups):
    for setup_name in setups:
        if setup_name not in BOOTSTRAP_SETUPS:
            print('[!!!!] Unknown setup for `syncbin bootstrap`: {!r}'.format(setup_name), file=sys.stderr)
            print('[ ** ] Available setups: {}'.format(', '.join(sorted(BOOTSTRAP_SETUPS))), file=sys.stderr)
            sys.exit(1)
    for setup_name in setups:
        BOOTSTRAP_SETUPS[setup_name]()

if __name__ == '__main__':
    try:
        arguments = docopt(__doc__, version='fenhl/syncbin ' + __version__)
    except NameError:
        arguments = {
            'bootstrap': True,
            '<setup>': 'python'
        }
    if arguments['bootstrap']:
        bootstrap(*arguments['<setup>'])
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
