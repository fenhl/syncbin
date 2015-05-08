#!/usr/bin/env python3

"""Update the Rust install and (if in a project directory) build the project.

Usage:
  rustup [options]
  rustup -h | --help
  rustup --version

Options:
  -h, --help     Print this message and exit.
  -q, --quiet    Don't print progress.
  --ignore-lock  Release and ignore the lock that prevents this script from running multiple times at once.
  --release      Build with the `--release' flag and skip tests.
  --run          Add a `cargo run' step at the end.
  --no-project   Only update Rust itself, don't attempt to update any git repo or cargo project.
  --version      Print version info and exit.
"""

import sys

import atexit
from docopt import docopt
import os
import subprocess
import time

try:
    with open(os.path.join(os.environ.get('GITDIR', '/opt/git'), 'github.com', 'fenhl', 'syncbin', 'master', 'version.txt')) as version_file:
        __version__ = version_file.read().strip()
except:
    __version__ = '0.0'

LOCKDIR = '/tmp/syncbin-rustup.lock'
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
    if arguments['--ignore-lock']:
        print('[ !! ]', 'releasing rustup lock', file=sys.stderr)
        os.rmdir(LOCKDIR)
    else:
        set_status(0, 'acquiring lock')
        while True:
            try:
                os.mkdir(LOCKDIR)
            except OSError:
                time.sleep(1) # lock exists, try again in a sec
            else:
                # lock acquired
                atexit.register(os.rmdir, LOCKDIR)
                break
    set_status(1, 'updating Rust nightly')
    with open('/dev/null', 'a') as dev_null:
        update_nightly = subprocess.Popen(['multirust', 'update', 'nightly'], stdout=dev_null, stderr=dev_null)
        if update_nightly.wait() != 0:
            print('[!!!!]', 'updating Rust nightly: failed', file=sys.stderr)
            sys.exit(update_nightly.returncode)
    set_status(3 if arguments['--no-project'] else 2, 'updating Rust beta   ')
    with open('/dev/null', 'a') as dev_null:
        update_beta = subprocess.Popen(['multirust', 'update', 'beta'], stdout=dev_null, stderr=dev_null)
        if update_beta.wait() != 0:
            print('[!!!!]', 'updating Rust beta: failed', file=sys.stderr)
            sys.exit(update_beta.returncode)
    if arguments['--no-project']:
        set_status(5, 'update complete   ')
        sys.exit()
    with open('/dev/null', 'a') as dev_null:
        if subprocess.call(['git', 'branch'], stdout=dev_null, stderr=dev_null) == 0:
            set_status(3, 'updating repo     ')
            subprocess.check_call(['git', 'fetch', '--quiet'])
            try:
                subprocess.check_call(['git', 'merge', '--quiet', 'FETCH_HEAD'], stdout=dev_null)
            except subprocess.CalledProcessError:
                subprocess.check_call(['git', 'merge', '--abort'])
                raise
        elif not QUIET:
            print('[ ** ]', 'not a git repo, skipping repo update step')
    set_status(4, 'updating crates')
    with open('/dev/null', 'a') as dev_null:
        update_crates = subprocess.Popen(['cargo', 'update'], stdout=dev_null)
        if update_crates.wait() != 0:
            print('[!!!!]', 'updating crates: failed', file=sys.stderr)
            sys.exit(update_crates.returncode)
    set_status(5, 'update complete')
    cargo_build = subprocess.Popen(['cargo', 'build'] + (['--release'] if arguments['--release'] else []))
    if cargo_build.wait() != 0:
        sys.exit(cargo_build.returncode)
    if arguments['--release']:
        exit_status = 0
    else:
        exit_status = subprocess.call(['cargo', 'test'])
    if exit_status == 0 and arguments['--run']:
        os.rmdir(LOCKDIR) # unlock
        try:
            sys.exit(subprocess.call(['cargo', 'run'] + (['--release'] if arguments['--release'] else [])))
        except KeyboardInterrupt:
            print()
            sys.exit(130)
    else:
        sys.exit(exit_status)
