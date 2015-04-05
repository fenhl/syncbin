#!/usr/bin/env python3

"""Update the Rust install and (if in a project directory) build the project.

Usage:
  rustup [options]
  rustup -h | --help
  rustup --version

Options:
  -h, --help    Print this message and exit.
  -q, --quiet   Don't print progress.
  --run         Add a `cargo run' step at the end.
  --no-project  Only update Rust itself, don't attempt to update any git repo or cargo project.
  --version     Print version info and exit.
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

QUIET = False

def set_status(progress, message, newline=False):
    if QUIET:
        return
    if progress >= 5:
        print('[ ok ]', message)
    else:
        print('[' + '=' * progress + '.' * (4 - progress) + ']', message, end='\n' if newline else '\r')

if __name__ == '__main__':
    arguments = docopt(__doc__, version='rustup from fenhl/syncbin ' + __version__)
    if arguments['--quiet']:
        QUIET = True
    set_status(0, 'updating Rust nightly')
    with open('/dev/null', 'a') as dev_null:
        update_nightly = subprocess.Popen(['multirust', 'update', 'nightly'], stdout=dev_null, stderr=dev_null)
        if update_nightly.wait() != 0:
            print('[ !! ]', 'updating Rust nightly: failed', file=sys.stderr)
            sys.exit(update_nightly.returncode)
    set_status(2 if arguments['--no-project'] else 1, 'updating Rust beta   ')
    with open('/dev/null', 'a') as dev_null:
        update_beta = subprocess.Popen(['multirust', 'update', 'beta'], stdout=dev_null, stderr=dev_null)
        if update_beta.wait() != 0:
            print('[ !! ]', 'updating Rust beta: failed', file=sys.stderr)
            sys.exit(update_beta.returncode)
    if arguments['--no-project']:
        set_status(5, 'update complete   ')
        sys.exit()
    with open('/dev/null', 'a') as dev_null:
        if subprocess.call(['git', 'branch'], stdout=dev_null, stderr=dev_null) == 0:
            set_status(2, 'updating repo     ')
            subprocess.check_call(['git', 'fetch', '--quiet'])
            set_status(3, 'updating repo')
            subprocess.check_call(['git', 'merge', '--quiet', 'FETCH_HEAD'], stdout=dev_null)
        elif not QUIET:
            print('[ ** ]', 'not a git repo, skipping repo update step')
    set_status(4, 'updating crates')
    with open('/dev/null', 'a') as dev_null:
        update_crates = subprocess.Popen(['cargo', 'update'], stdout=dev_null)
        if update_crates.wait() != 0:
            print('[ !! ]', 'updating crates: failed', file=sys.stderr)
            sys.exit(update_crates.returncode)
    set_status(5, 'update complete')
    cargo_build = subprocess.Popen(['cargo', 'build'])
    if cargo_build.wait() != 0:
        sys.exit(cargo_build.returncode)
    exit_status = subprocess.call(['cargo', 'test'])
    if exit_status == 0 and arguments['--run']:
        sys.exit(subprocess.call(['cargo', 'run']))
    else:
        sys.exit(exit_status)
