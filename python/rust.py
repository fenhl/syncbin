#!/usr/bin/env python3

"""Update the Rust install and (if in a project directory) build the project.

Usage:
  rust [options]
  rust current
  rust default
  rust override
  rust rprompt
  rust -h | --help
  rust --version

Options:
  -R, --release        Build with the `--release' flag and skip tests.
  -T, --no-test        Skip the `cargo test` step.
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

import pathlib
import sys

sys.path += ['/opt/py', str(pathlib.Path.home() / 'py')]

import basedir
import docopt
import os
import re
import shutil
import subprocess
import syncbin

try:
    with pathlib.Path(os.environ.get('GITDIR', '/opt/git'), 'github.com', 'fenhl', 'syncbin', 'master', 'version.txt').open() as version_file:
        __version__ = version_file.read().strip()
except Exception:
    __version__ = '0.0'

QUIET = False

def current_toolchain(cwd=None):
    return override(cwd) or default_toolchain()

def default_toolchain():
    show_default = subprocess.Popen(env('rustup', 'show'), stdout=subprocess.PIPE)
    out, _ = show_default.communicate(timeout=5)
    for line in out.decode('utf-8').split('\n'):
        if line == 'no active toolchain':
            return None
        if '(default)' not in line:
            continue
        match = line.split('-')[0]
        for formatting_prefix in {'\x1b(B\x1b[m', '\x1b[m\x0f'}:
            if line.startswith(formatting_prefix):
                match = match[len(formatting_prefix):]
        return match
    else:
        raise NotImplementedError('Failed to parse default toolchain')

def env(*args):
    return ['/usr/bin/env', 'PATH={}:{}'.format(pathlib.Path.home() / '.cargo' / 'bin', os.environ['PATH']), *args]

def override(cwd=None):
    if cwd is None:
        cwd = pathlib.Path().resolve()
    overrides_out = subprocess.run(env('rustup', 'override', 'list'), stdout=subprocess.PIPE, check=True, encoding='utf-8').stdout
    if overrides_out == 'no overrides\n':
        return
    for line in overrides_out.splitlines():
        path, override = line.rsplit(None, 1)
        path = pathlib.Path(path).resolve()
        if path == cwd or path in cwd.parents:
            return override.split('-')[0]

def quiet():
    if QUIET:
        yield '--quiet'

def rprompt(cwd=None):
    if cwd is None:
        cwd = pathlib.Path().resolve()
    overrides_out = subprocess.run(env('rustup', 'override', 'list'), stdout=subprocess.PIPE, check=True, encoding='utf-8').stdout
    if '(not a directory)' in overrides_out:
        return '[rust: nonexistent]'
    try:
        result = override(cwd)
    except RuntimeError as e:
        return '[rust: {}]'.format(e)
    else:
        if result is not None:
            return '[rust: {}]'.format(result)

def rustup_update(toolchain=None, timeout=300):
    if toolchain is None:
        toolchain = current_toolchain()
    with syncbin.lock('rust'): # see https://github.com/rust-lang/rustup.rs/issues/988
        update_popen = subprocess.Popen(env('rustup', 'update', toolchain), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        if update_popen.wait(timeout=timeout) != 0:
            print('[!!!!]', 'updating Rust {}: failed'.format(toolchain), file=sys.stderr)
            sys.exit(update_popen.returncode)
    except subprocess.TimeoutExpired:
        update_popen.terminate()
        print('[!!!!]', 'updating Rust {}: timed out'.format(toolchain), file=sys.stderr)
        sys.exit(update_popen.returncode)
    with syncbin.lock('rust'): # see https://github.com/rust-lang/rustup.rs/issues/988
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
        subprocess.check_call(['git', 'fetch', *quiet()], cwd=str(path))
        try:
            subprocess.check_call(['git', 'merge', *quiet(), 'FETCH_HEAD'], stdout=subprocess.DEVNULL, cwd=str(path))
        except subprocess.CalledProcessError:
            subprocess.check_call(['git', 'merge', '--abort'], cwd=str(path))
            raise
    elif not QUIET:
        print('[ ** ]', 'not a git repo, skipping repo update step')
    if (path / 'Cargo.lock').exists(): # `cargo update` complains if no Cargo.lock exists yet
        if arguments['--crates'] or subprocess.call(['git', 'check-ignore', 'Cargo.lock'], stdout=subprocess.DEVNULL, cwd=str(path)) == 0:
            set_status(4, 'updating crates     ')
            update_crates = subprocess.Popen(env('cargo', 'update', *quiet()), cwd=str(path))
            if update_crates.wait() != 0:
                print('[!!!!]', 'updating crates: failed', file=sys.stderr)
                return update_crates.returncode
        elif not QUIET:
            print('[ ** ]', 'Cargo.lock tracked by git, skipping crates update step, `--crates` to override')
    set_status(5, 'update complete')
    cargo_build = subprocess.Popen(env('cargo', 'build', *(['--release'] if arguments['--release'] else []), *quiet()), cwd=str(path))
    if cargo_build.wait() != 0:
        return cargo_build.returncode
    if arguments['--release'] or arguments['--no-test']:
        exit_status = 0
    else:
        exit_status = subprocess.call(env('cargo', 'test', *quiet()), cwd=str(path))
    if exit_status == 0 and arguments['--run']:
        try:
            return subprocess.call(env('cargo', 'run', *(['--release'] if arguments['--release'] else []), *quiet()), cwd=str(path))
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
    if arguments['override']:
        output = override()
        if output is None:
            sys.exit()
        print(output)
        sys.exit(1)
    if arguments['rprompt']:
        output = rprompt()
        if output is not None:
            print(output)
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
        rustup_update('nightly', timeout=timeout)
        set_status(1, 'updating Rust beta   ')
        rustup_update('beta', timeout=timeout)
        set_status(2, 'updating Rust stable')
        rustup_update('stable', timeout=timeout)
    else:
        toolchain = current_toolchain()
        set_status(0, 'updating Rust {}'.format(toolchain))
        rustup_update(toolchain, timeout=timeout)
    if arguments['--no-project']:
        set_status(5, 'update complete      ')
    elif arguments['--all-projects']:
        set_status(3, 'updating installed crates')
        subprocess.check_call(env('cargo', 'install-update', '--all', '--git'), stdout=subprocess.DEVNULL)
        subprocess.run(['rm', '-rf', '/tmp/cargo-update'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # for some reason, cargo-update sometimes doesn't clean up its tempfiles?
        for path in map(pathlib.Path, basedir.config_dirs('fenhl/syncbin.json').json(base={}).get('rust', {}).get('projects', [])):
            exit_status = update_project(path, arguments)
            if exit_status != 0:
                sys.exit(exit_status)
    else:
        sys.exit(update_project(pathlib.Path(), arguments))
