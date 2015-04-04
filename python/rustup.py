#!/usr/bin/env python3

"""Update the Rust install and (if in a project directory) build the project.

Usage:
  rustup [--run]
  rustup -h | --help
  rustup --version

Options:
  -h, --help  Print this message and exit.
  --run       Add a `cargo run' step at the end.
  --version   Print version info and exit.
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

def set_status(progress, message, newline=False):
    if progress >= 5:
        print('[ ok ]', message)
    else:
        print('[' + '=' * progress + '.' * (4 - progress) + ']', message, end='\n' if newline else '\r')

if __name__ == '__main__':
    arguments = docopt(__doc__, version='rustup from fenhl/syncbin ' + __version__)
    set_status(0, 'updating Rust nightly')
    with open('/dev/null', 'a') as dev_null:
        update_nightly = subprocess.Popen(['multirust', 'update', 'nightly'], stdout=dev_null, stderr=dev_null)
        if update_nightly.wait() != 0:
            print('[ !! ]', 'updating Rust nightly: failed')
            sys.exit(update_nightly.returncode)
    set_status(1, 'updating Rust beta   ')
    with open('/dev/null', 'a') as dev_null:
        update_beta = subprocess.Popen(['multirust', 'update', 'beta'], stdout=dev_null, stderr=dev_null)
        if update_beta.wait() != 0:
            print('[ !! ]', 'updating Rust beta: failed')
            sys.exit(update_beta.returncode)
    with open('/dev/null', 'a') as dev_null:
        if subprocess.call(['git', 'branch'], stdout=dev_null, stderr=dev_null) == 0:
            set_status(2, 'updating repo     ')
            subprocess.check_call(['git', 'fetch', '--quiet'])
            set_status(3, 'updating repo')
            subprocess.check_call(['git', 'merge', '--quiet', 'FETCH_HEAD'], stdout=dev_null)
        else:
            print('[ ** ]', 'not a git repo, skipping repo update step')
    set_status(4, 'updating crates')
    with open('/dev/null', 'a') as dev_null:
        update_crates = subprocess.Popen(['cargo', 'update'], stdout=dev_null)
        if update_crates.wait() != 0:
            print('[ !! ]', 'updating crates: failed')
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
