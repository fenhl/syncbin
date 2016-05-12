#!/usr/bin/env python3

"""Update the Rust install and (if in a project directory) build the project.

Usage:
  rs [options]
  rs -h | --help
  rs --version

Options:
  -R, --release     Build with the `--release' flag and skip tests.
  -c, --crates      Update Cargo.lock even if not ignored.
  -h, --help        Print this message and exit.
  -q, --quiet       Don't print progress.
  -r, --run         Add a `cargo run' step at the end.
  --all-toolchains  Update all Rust toolchains.
  --ignore-lock     Release and ignore the lock that prevents this script from running multiple times at once.
  --no-project      Only update Rust itself, don't attempt to update any git repo or cargo project.
  --skip-if-locked  If another instance of the script is already running, do nothing.
  --version         Print version info and exit.
"""

import sys

import atexit
from docopt import docopt
import os
import re
import subprocess
import time

try:
    with open(os.path.join(os.environ.get('GITDIR', '/opt/git'), 'github.com', 'fenhl', 'syncbin', 'master', 'version.txt')) as version_file:
        __version__ = version_file.read().strip()
except:
    __version__ = '0.0'

LOCKDIR = '/tmp/syncbin-rs.lock'
QUIET = False

def current_toolchain(cwd=None):
    show_override = subprocess.Popen(['rustup', 'override', 'list'], stdout=subprocess.PIPE, cwd=cwd)
    out, _ = show_override.communicate(timeout=5)
    for line in out.decode('utf-8').split('\n'):
        if line == 'no overrides':
            return 'stable'
        match = re.search('\t(.*?)-', line)
        if match:
            return match.group(1)
    else:
        raise ValueError('Current toolchain could not be determined')

def multirust_update(toolchain=None):
    if toolchain is None:
        toolchain = current_toolchain()
    update_popen = subprocess.Popen(['rustup', 'update', toolchain], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        if update_popen.wait(timeout=300) != 0:
            print('[!!!!]', 'updating Rust {}: failed'.format(toolchain), file=sys.stderr)
            sys.exit(update_popen.returncode)
    except subprocess.TimeoutExpired:
        update_popen.terminate()
        print('[!!!!]', 'updating Rust {}: timed out'.format(toolchain), file=sys.stderr)
        sys.exit(update_popen.returncode)

def set_status(progress, message, newline=False):
    if QUIET:
        return
    if progress >= 5:
        print('[ ok ]', message)
    else:
        print('[' + '=' * progress + '.' * (4 - progress) + ']', message, end='\n' if newline else '\r')

if __name__ == '__main__':
    arguments = docopt(__doc__, version='rs from fenhl/syncbin ' + __version__)
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
                if arguments['--skip-if-locked']:
                    sys.exit()
                time.sleep(1) # lock exists, try again in a sec
            else:
                # lock acquired
                atexit.register(os.rmdir, LOCKDIR)
                break
    if arguments['--all-toolchains']:
        set_status(0, 'updating Rust nightly')
        multirust_update('nightly')
        set_status(1, 'updating Rust beta   ')
        multirust_update('beta')
        set_status(2, 'updating Rust stable')
        multirust_update('stable')
    else:
        toolchain = current_toolchain()
        set_status(0, 'updating Rust {}'.format(toolchain))
        multirust_update(toolchain)
    if arguments['--no-project']:
        set_status(5, 'update complete      ')
        sys.exit()
    with open('/dev/null', 'a') as dev_null:
        if subprocess.call(['git', 'branch'], stdout=dev_null, stderr=dev_null) == 0:
            set_status(3, 'updating repo        ')
            subprocess.check_call(['git', 'fetch', '--quiet'])
            try:
                subprocess.check_call(['git', 'merge', '--quiet', 'FETCH_HEAD'], stdout=dev_null)
            except subprocess.CalledProcessError:
                subprocess.check_call(['git', 'merge', '--abort'])
                raise
        elif not QUIET:
            print('[ ** ]', 'not a git repo, skipping repo update step')
    with open('/dev/null', 'a') as dev_null:
        if os.path.exists('Cargo.lock'): # `cargo update` complains if no Cargo.lock exists yet
            if arguments['--crates'] or subprocess.call(['git', 'check-ignore', 'Cargo.lock'], stdout=dev_null) == 0:
                set_status(4, 'updating crates     ')
                update_crates = subprocess.Popen(['cargo', 'update'], stdout=dev_null)
                if update_crates.wait() != 0:
                    print('[!!!!]', 'updating crates: failed', file=sys.stderr)
                    sys.exit(update_crates.returncode)
            elif not QUIET:
                print('[ ** ]', 'Cargo.lock tracked by git, skipping crates update step, `--crates` to override')
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
        atexit.unregister(os.rmdir)
        try:
            sys.exit(subprocess.call(['cargo', 'run'] + (['--release'] if arguments['--release'] else [])))
        except KeyboardInterrupt:
            print()
            sys.exit(130)
        except ProcessLookupError:
            print()
            sys.exit()
    else:
        sys.exit(exit_status)
