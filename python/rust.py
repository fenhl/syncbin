#!/usr/bin/env python3

"""Update the Rust install and (if in a project directory) build the project.

Usage:
  rust [options]
  rust current
  rust default
  rust -h | --help
  rust --version

Options:
  -R, --release        Build with the `--release' flag and skip tests.
  -c, --crates         Update Cargo.lock even if not ignored.
  -h, --help           Print this message and exit.
  -q, --quiet          Don't print progress.
  -r, --run            Add a `cargo run' step at the end.
  --all-projects       Update all git repos listed at $XDG_CONFIG_DIRS/fenhl/syncbin.json instead of just the current directory.
  --all-toolchains     Update all Rust toolchains.
  --no-project         Only update Rust itself, don't attempt to update any git repo or cargo project.
  --no-timeout         Don't automatically abort the update process of a toolchain. Overrides `--timeout'.
  --timeout=<seconds>  The update process of a toolchain is aborted after this many seconds [Default: 300].
  --version            Print version info and exit.
"""

import sys

sys.path.append('/opt/py')

import basedir
import docopt
import os
import pathlib
import re
import subprocess

try:
    with pathlib.Path(os.environ.get('GITDIR', '/opt/git'), 'github.com', 'fenhl', 'syncbin', 'master', 'version.txt').open() as version_file:
        __version__ = version_file.read().strip()
except Exception:
    __version__ = '0.0'

QUIET = False

def current_toolchain(cwd=None):
    show_override = subprocess.Popen(env('rustup', 'override', 'list'), stdout=subprocess.PIPE, cwd=cwd)
    out, _ = show_override.communicate(timeout=5)
    for line in out.decode('utf-8').split('\n'):
        if line == 'no overrides':
            return default_toolchain()
        match = re.search('\t(.*?)-', line)
        if match:
            return match.group(1)
    else:
        raise ValueError('Current toolchain could not be determined')

def default_toolchain():
    show_default = subprocess.Popen(env('rustup', 'show'), stdout=subprocess.PIPE)
    out, _ = show_default.communicate(timeout=5)
    for line in out.decode('utf-8').split('\n'):
        if line == 'no active toolchain':
            return None
        if '(default)' not in line:
            continue
        if line.startswith('stable-') or line.startswith('\x1b(B\x1b[mstable-') or line.startswith('\x1b[m\x0fstable-'):
            return 'stable'
        elif line.startswith('beta-') or line.startswith('\x1b(B\x1b[mbeta-') or line.startswith('\x1b[m\x0fbeta-'):
            return 'beta'
    else:
        raise NotImplementedError('Failed to parse default toolchain')

def env(*args):
    return ['/usr/bin/env', 'PATH={}:{}'.format(pathlib.Path.home() / '.cargo' / 'bin', os.environ['PATH']), *args]

def multirust_update(toolchain=None, timeout=300):
    if toolchain is None:
        toolchain = current_toolchain()
    update_popen = subprocess.Popen(env('rustup', 'update', toolchain), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        if update_popen.wait(timeout=timeout) != 0:
            print('[!!!!]', 'updating Rust {}: failed'.format(toolchain), file=sys.stderr)
            sys.exit(update_popen.returncode)
    except subprocess.TimeoutExpired:
        update_popen.terminate()
        print('[!!!!]', 'updating Rust {}: timed out'.format(toolchain), file=sys.stderr)
        sys.exit(update_popen.returncode)
    subprocess.check_call(env('rustup', 'self', 'update'), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def set_status(progress, message, newline=False):
    if QUIET:
        return
    if progress >= 5:
        print('[ ok ]', message)
    else:
        print('[' + '=' * progress + '.' * (4 - progress) + ']', message, end='\n' if newline else '\r')

def update_project(path, arguments):
    if subprocess.call(['git', 'branch'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=str(path)) == 0:
        set_status(3, 'updating repo        ')
        subprocess.check_call(['git', 'fetch', '--quiet'], cwd=str(path))
        try:
            subprocess.check_call(['git', 'merge', '--quiet', 'FETCH_HEAD'], stdout=subprocess.DEVNULL, cwd=str(path))
        except subprocess.CalledProcessError:
            subprocess.check_call(['git', 'merge', '--abort'], cwd=str(path))
            raise
    elif not QUIET:
        print('[ ** ]', 'not a git repo, skipping repo update step')
    if pathlib.Path('Cargo.lock').exists(): # `cargo update` complains if no Cargo.lock exists yet
        if arguments['--crates'] or subprocess.call(['git', 'check-ignore', 'Cargo.lock'], stdout=subprocess.DEVNULL, cwd=str(path)) == 0:
            set_status(4, 'updating crates     ')
            update_crates = subprocess.Popen(env('cargo', 'update', '--quiet'), cwd=str(path))
            if update_crates.wait() != 0:
                print('[!!!!]', 'updating crates: failed', file=sys.stderr)
                return update_crates.returncode
        elif not QUIET:
            print('[ ** ]', 'Cargo.lock tracked by git, skipping crates update step, `--crates` to override')
    set_status(5, 'update complete')
    cargo_build = subprocess.Popen(env('cargo', 'build', *(['--release'] if arguments['--release'] else []), *(['--quiet'] if QUIET else [])), cwd=str(path))
    if cargo_build.wait() != 0:
        return cargo_build.returncode
    if arguments['--release']:
        exit_status = 0
    else:
        exit_status = subprocess.call(env('cargo', 'test', *(['--quiet'] if QUIET else [])), cwd=str(path))
    if exit_status == 0 and arguments['--run']:
        try:
            return subprocess.call(env('cargo', 'run', *(['--release'] if arguments['--release'] else []), *(['--quiet'] if QUIET else [])), cwd=str(path))
        except KeyboardInterrupt:
            print()
            return 130
        except ProcessLookupError:
            print()
            return 0
    else:
        return exit_status

if __name__ == '__main__':
    arguments = docopt.docopt(__doc__, version='rust from fenhl/syncbin ' + __version__)
    if arguments['current']:
        print(current_toolchain())
        sys.exit()
    if arguments['default']:
        print(default_toolchain())
        sys.exit()
    if arguments['--quiet']:
        QUIET = True
    if arguments['--no-timeout']:
        timeout = None
    else:
        timeout = int(arguments['--timeout'])
    timeout
    if arguments['--all-toolchains']:
        set_status(0, 'updating Rust nightly')
        multirust_update('nightly', timeout=timeout)
        set_status(1, 'updating Rust beta   ')
        multirust_update('beta', timeout=timeout)
        set_status(2, 'updating Rust stable')
        multirust_update('stable', timeout=timeout)
    else:
        toolchain = current_toolchain()
        set_status(0, 'updating Rust {}'.format(toolchain))
        multirust_update(toolchain, timeout=timeout)
    if arguments['--no-project']:
        set_status(5, 'update complete      ')
    elif arguments['--all-projects']:
        for path in map(pathlib.Path, basedir.config_dirs('fenhl/syncbin.json').json(base={}).get('rust', {}).get('projects', [])):
            exit_status = update_project(path, arguments)
            if exit_status != 0:
                sys.exit(exit_status)
    else:
        sys.exit(update_project(pathlib.Path(), arguments))
