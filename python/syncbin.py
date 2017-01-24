#!/usr/bin/env python3

"""Config and helper tool for Fenhl's syncbin.

Usage:
  syncbin bootstrap [<setup>...]
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

import contextlib
import getpass
import pathlib
import os
import subprocess
import json
import platform
import stat

try:
    from docopt import docopt
except ImportError:
    if __name__ == '__main__':
        print('[ !! ] docopt not installed, defaulting to `syncbin bootstrap python`', file=sys.stderr)

BOOTSTRAP_SETUPS = {}

def git_dir(existing_only=True):
    with contextlib.suppress(ImportError):
        import gitdir

        return gitdir.GITDIR
    if existing_only:
        if 'GITDIR' in os.environ and pathlib.Path(os.environ['GITDIR']).exists():
            return pathlib.Path(os.environ['GITDIR'])
        elif pathlib.Path('/opt/git').exists():
            return pathlib.Path('/opt/git')
        elif pathlib.Path('{}/git'.format(os.environ['HOME'])).exists():
            return pathlib.Path('{}/git'.format(os.environ['HOME']))
        else:
            raise FileNotFoundError('No existing gitdir found')
    else:
        return pathlib.Path(os.environ.get('GITDIR', '/opt/git' if root() else '{}/git'.format(os.environ['HOME'])))

def py_dir():
    return pathlib.Path('/opt/py' if root() else '{}/py'.format(os.environ['HOME']))

def root():
    if getpass.getuser() == 'root':
        return True
    return subprocess.call(['sudo', '-n', 'true'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

def version():
    try:
        with (git_dir() / 'github.com' / 'fenhl' / 'syncbin' / 'master' / 'version.txt').open() as version_file:
            return version_file.read().strip()
    except:
        return '0.0'

def which(cmd):
    try:
        return subprocess.check_output(['which', cmd], stderr=subprocess.DEVNULL).decode('utf-8')[:-1]
    except subprocess.CalledProcessError:
        return None

def yesno(question):
    answer = input('[ ?? ] {} [y/n] '.format(question))
    while True:
        if answer.lower() in ('y', 'yes'):
            return True
        elif answer.lower() in ('n', 'no'):
            return False
        answer = input('[ ?? ] unrecognized answer, type “yes” or “no”: ')

__version__ = version()

def bootstrap_setup(setup_name):
    def inner_wrapper(f):
        def test_installed(is_installed):
            f.is_installed = is_installed
            return f
        def requires(*reqs):
            f.requirements += reqs
            return f

        BOOTSTRAP_SETUPS[setup_name] = f
        f.is_installed = lambda: None
        f.test_installed = test_installed
        f.requirements = []
        f.requires = requires
        return f
    return inner_wrapper

@bootstrap_setup('brew')
def bootstrap_brew():
    """Installs various utilities for OS X using Homebrew"""
    try:
        subprocess.check_call(['brew', 'install', 'git', 'jq', 'ruby', 'terminal-notifier'])
    except subprocess.CalledProcessError:
        subprocess.check_call(['brew', 'link', '--overwrite', 'ruby'])
    subprocess.check_call(['brew', 'cask', 'install', 'qlmarkdown'])

@bootstrap_brew.test_installed
def bootstrap_brew():
    if which('brew') is None:
        return False
    return len(json.loads(subprocess.check_output(['brew', 'info', '--json=v1', 'terminal-notifier']).decode('utf-8'))[0]['installed']) > 0

@bootstrap_setup('debian-root')
def bootstrap_debian_root():
    """Essential setup for Debian systems with root access"""
    apt_packages = [
        'exiftool',
        'needrestart',
        'ntp',
        'ruby',
        'ruby-dev',
        'screen',
        'ssmtp' #TODO configure
    ]
    if getpass.getuser() == 'root':
        subprocess.check_call(['apt-get', 'install'] + apt_packages)
        subprocess.check_call(['chmod', 'u+s', which('ping')])
    else:
        subprocess.check_call(['sudo', 'apt-get', 'install'] + apt_packages)
        subprocess.check_call(['sudo', 'chmod', 'u+s', which('ping')])

@bootstrap_debian_root.test_installed
def bootstrap_debian_root():
    if getpass.getuser() == 'root':
        try:
            subprocess.check_call(['systemctl', '-q', 'is-active', 'ntp'], stderr=subprocess.DEVNULL)
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False
        else:
            return True
    else:
        try:
            subprocess.check_call(['sudo', '-n', 'true'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            return None
        try:
            subprocess.check_call(['sudo', '-n', 'systemctl', '-q', 'is-active', 'ntp'], stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            return False
        else:
            return True

@bootstrap_setup('finder')
def bootstrap_finder():
    """Configure useful defaults for Finder on OS X"""
    print('[....] configuring Finder', end='\r', flush=True)
    subprocess.check_call(['defaults', 'write', '-g', 'NSScrollViewRubberbanding', '-int', '0'])
    subprocess.check_call(['defaults', 'write', 'com.apple.finder', 'AppleShowAllFiles', '-bool', 'true'])
    subprocess.check_call(['defaults', 'write', 'com.apple.finder', '_FXShowPosixPathInTitle', '-bool', 'true'])
    print('[ ok ]')
    print('[....] restarting Finder', end='\r', flush=True)
    subprocess.check_call(['killall', 'Finder'])
    print('[ ok ]')
    print('[....] configuring Dock', end='\r', flush=True)
    subprocess.check_call(['defaults', 'write', 'com.apple.Dock', 'showhidden', '-bool', 'true'])
    print('[ ok ]')
    print('[....] restarting Dock', end='\r', flush=True)
    subprocess.check_call(['killall', 'Dock'])
    print('[ ok ]')

@bootstrap_finder.test_installed
def bootstrap_finder():
    try:
        return subprocess.check_output(['defaults', 'read', 'com.apple.finder', '_FXShowPosixPathInTitle'], stderr=subprocess.STDOUT) == b'1\n'
    except FileNotFoundError:
        return None
    except subprocess.CalledProcessError:
        return False

@bootstrap_setup('gitdir')
def bootstrap_gitdir():
    """Installs `gitdir`. Requires the `python` setup."""
    gitdir_gitdir = git_dir(existing_only=False) / 'github.com' / 'fenhl' / 'gitdir'
    if not gitdir_gitdir.exists():
        gitdir_gitdir.mkdir(parents=True)
    if not (gitdir_gitdir / 'master').exists():
        subprocess.check_call(['git', 'clone', 'https://github.com/fenhl/gitdir.git', 'master'], cwd=str(git_dir() / 'github.com' / 'fenhl' / 'gitdir'))
    if not (py_dir() / 'gitdir').exists():
        if not py_dir().exists():
            sys.exit('[!!!!] run `syncbin bootstrap python` first')
        try:
            (py_dir() / 'gitdir').symlink_to(gitdir_gitdir / 'master' / 'gitdir')
        except PermissionError:
            subprocess.check_call(['sudo', 'ln', '-s', str(gitdir_gitdir / 'master' / 'gitdir'), str(py_dir() / 'gitdir')])

@bootstrap_gitdir.test_installed
def bootstrap_gitdir():
    try:
        sys.path.append(str(py_dir()))
        import gitdir
    except ImportError:
        return False
    else:
        return True

@bootstrap_setup('macbook')
def bootstrap_macbook():
    """Installs `batcharge` for MacBooks."""
    if hasattr(pathlib.Path, 'home'): # Python 3.5 and above
        bin_path = (pathlib.Path.home() / 'bin')
    else:
        bin_path = pathlib.Path(input('[ ?? ] where should the `batcharge` symlink be created? '))
    if not bin_path.exists():
        bin_path.mkdir()
    batcharge = bin_path / 'batcharge'
    batcharge.symlink_to(git_dir() / 'fenhl.net' / 'syncbin-private' / 'master' / 'bin' / 'batcharge-macbook')

bootstrap_macbook.requires('syncbin-private')

@bootstrap_macbook.test_installed
def bootstrap_macbook():
    if not hasattr(pathlib.Path, 'home'): # Python 3.4 and below
        return None
    config_path = (pathlib.Path.home() / 'bin' / 'batcharge')
    if not config_path.is_symlink():
        return False
    return config_path.resolve() == git_dir() / 'fenhl.net' / 'syncbin-private' / 'master' / 'python' / 'batcharge_macbook.py'

@bootstrap_setup('no-battery')
def bootstrap_no_battery():
    """Installs `batcharge` for devices without batteries."""
    if hasattr(pathlib.Path, 'home'): # Python 3.5 and above
        bin_path = (pathlib.Path.home() / 'bin')
    else:
        bin_path = pathlib.Path(input('[ ?? ] where should `batcharge` be saved? '))
    if not bin_path.exists():
        bin_path.mkdir()
    batcharge = bin_path / 'batcharge'
    with batcharge.open('w') as f:
        print('#!/bin/sh\n\nexit 0', file=f)
    batcharge.chmod(batcharge.stat().st_mode | stat.S_IEXEC)

@bootstrap_no_battery.test_installed
def bootstrap_no_battery():
    if not hasattr(pathlib.Path, 'home'): # Python 3.4 and below
        return None
    if not (pathlib.Path.home() / 'bin' / 'batcharge').exists():
        return False
    with (pathlib.Path.home() / 'bin' / 'batcharge').open() as batcharge_f:
        return batcharge_f.read == '#!/bin/sh\n\nexit 0\n'

@bootstrap_setup('python')
def bootstrap_python():
    """Installs Python modules and creates `/opt/py`. Must be run twice, once before the gitdir setup, once after."""
    pip_packages = [
        'blessings',
        'docopt',
        'python-mpd2',
        'pytz',
        'requests',
        'tzlocal'
    ]
    if root():
        subprocess.check_call(['pip3', 'install'] + pip_packages)
    else:
        subprocess.check_call(['pip3', 'install', '--user'] + pip_packages)
    if not py_dir().exists():
        try:
            py_dir().mkdir()
        except PermissionError:
            subprocess.check_call(['sudo', 'mkdir', str(py_dir())])
    try:
        sys.path.append(str(py_dir()))
        import gitdir.host
    except ImportError:
        print('[ ** ] run `syncbin bootstrap gitdir`, then re-run `syncbin bootstrap python` to install essentials from github')
    else:
        gitdir.host.by_name('github.com').clone('fenhl/python-xdg-basedir')
        gitdir.host.by_name('github.com').clone('fenhl/fancyio')
        gitdir.host.by_name('github.com').clone('fenhl/lazyjson')
        gitdir.host.by_name('github.com').clone('fenhl/python-timespec')
        if root() and getpass.getuser() != 'root':
            if not (py_dir() / 'basedir.py').exists():
                subprocess.check_output(['sudo', 'ln', '-s', str(git_dir() / 'github.com' / 'fenhl' / 'python-xdg-basedir' / 'master' / 'basedir.py'), str(py_dir() / 'basedir.py')])
            if not (py_dir() / 'fancyio.py').exists():
                subprocess.check_output(['sudo', 'ln', '-s', str(git_dir() / 'github.com' / 'fenhl' / 'fancyio' / 'master' / 'fancyio.py'), str(py_dir() / 'fancyio.py')])
            if not (py_dir() / 'lazyjson.py').exists():
                subprocess.check_output(['sudo', 'ln', '-s', str(git_dir() / 'github.com' / 'fenhl' / 'lazyjson' / 'master' / 'lazyjson.py'), str(py_dir() / 'lazyjson.py')])
            if not (py_dir() / 'timespec').exists():
                subprocess.check_output(['sudo', 'ln', '-s', str(git_dir() / 'github.com' / 'fenhl' / 'python-timespec' / 'master' / 'timespec'), str(py_dir() / 'timespec')])
        else:
            if not (py_dir() / 'basedir.py').exists():
                (py_dir() / 'basedir.py').symlink_to(git_dir() / 'github.com' / 'fenhl' / 'python-xdg-basedir' / 'master' / 'basedir.py')
            if not (py_dir() / 'fancyio.py').exists():
                (py_dir() / 'fancyio.py').symlink_to(git_dir() / 'github.com' / 'fenhl' / 'fancyio' / 'master' / 'fancyio.py')
            if not (py_dir() / 'lazyjson.py').exists():
                (py_dir() / 'lazyjson.py').symlink_to(git_dir() / 'github.com' / 'fenhl' / 'lazyjson' / 'master' / 'lazyjson.py')
            if not (py_dir() / 'timespec').exists():
                (py_dir() / 'timespec').symlink_to(git_dir() / 'github.com' / 'fenhl' / 'python-timespec' / 'master' / 'timespec')

@bootstrap_python.test_installed
def bootstrap_python():
    try:
        sys.path.append(str(py_dir()))
        import basedir, blessings, docopt, gitdir, lazyjson, requests
    except ImportError:
        return False
    else:
        return True

@bootstrap_setup('rust')
def bootstrap_rust():
    """Installs Rust via `rustup`."""
    #try:
    #    import requests
    #except ImportError:
    #    sys.exit('[!!!!] missing requests, run `syncbin bootstrap python` first')
    #response = requests.get('https://sh.rustup.rs/', stream=True)
    #response.raise_for_status()
    sys.exit(subprocess.call('curl https://sh.rustup.rs -sSf | sh -s -- --no-modify-path', shell=True))

@bootstrap_rust.test_installed
def bootstrap_rust():
    return which('rustup') is not None

@bootstrap_setup('ssh')
def bootstrap_ssh():
    """Symlinks the `syncbin` SSH config file, and installs `ssh-copy-id` using Homebrew."""
    if hasattr(pathlib.Path, 'home'): # Python 3.5 and above
        config_path = (pathlib.Path.home() / '.ssh' / 'config')
    else:
        config_path = pathlib.Path(input('[ ?? ] where should the SSH config be saved? '))
    config_path.symlink_to(git_dir() / 'github.com' / 'fenhl' / 'syncbin' / 'master' / 'config' / 'ssh')
    config_path.chmod(0o600) # http://serverfault.com/a/253314
    if platform.system() == 'Darwin' and which('ssh-copy-id') is None:
        subprocess.check_call(['brew', 'install', 'ssh-copy-id'])

@bootstrap_ssh.test_installed
def bootstrap_ssh():
    if not hasattr(pathlib.Path, 'home'): # Python 3.4 and below
        return None
    config_path = (pathlib.Path.home() / '.ssh' / 'config')
    if not config_path.is_symlink():
        return False
    return config_path.resolve() == git_dir() / 'github.com' / 'fenhl' / 'syncbin' / 'master' / 'config' / 'ssh'

@bootstrap_setup('sudo')
def bootstrap_sudo():
    """Configures passwordless `sudo`."""
    sudoers_d = pathlib.Path('/etc/sudoers.d')
    if not sudoers_d.exists():
        subprocess.check_call(['sudo', 'mkdir', '-p', str(sudoers_d)])
    print('[ ** ] For passwordless login, insert the following line into the opened document:')
    print('fenhl ALL=(ALL) NOPASSWD: ALL')
    input('[ ?? ] Press return to continue')
    subprocess.check_call(['sudo', 'nano', str(sudoers_d / 'fenhl')])

@bootstrap_sudo.test_installed
def bootstrap_sudo():
    try:
        subprocess.check_call(['sudo', '-n', 'true'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return False
    else:
        return True

@bootstrap_setup('syncbin-private')
def bootstrap_syncbin_private():
    """Installs the private `syncbin` extensions."""
    sys.path.append(str(py_dir()))
    import gitdir.host

    try:
        gitdir.host.by_name('fenhl.net').clone('syncbin-private')
    except PermissionError:
        sys.exit('[!!!!] Permission denied. Fix /opt/git permissions, then try again.')

bootstrap_syncbin_private.requires('gitdir')

@bootstrap_syncbin_private.test_installed
def bootstrap_syncbin_private():
    return (git_dir() / 'fenhl.net' / 'syncbin-private' / 'master').is_dir()

@bootstrap_setup('t')
def bootstrap_t():
    """Installs the Twitter CLI `t`."""
    import gitdir.host

    try:
        gitdir.host.by_name('github.com').clone('sferik/t')
    except PermissionError:
        sys.exit('[!!!!] Permission denied. Fix /opt/git permissions, then try again.')
    if root() and getpass.getuser() != 'root':
        subprocess.check_call(['sudo', 'gem', 'install', 't'])
    else:
        subprocess.check_call(['gem', 'install', 't'])
    subprocess.check_call(['t', 'authorize', '--display-uri'])

@bootstrap_t.test_installed
def bootstrap_t():
    return which('t') is not None

@bootstrap_setup('zsh')
def bootstrap_zsh():
    """Installs useful extensions for Zsh."""
    sys.path.append(str(py_dir()))
    import gitdir.host

    gitdir.host.by_name('github.com').clone('zsh-users/zsh-syntax-highlighting')
    if yesno('install oh-my-zsh?'):
        gitdir.host.by_name('github.com').clone('robbyrussell/oh-my-zsh')
    if platform.system() == 'Darwin' and which('zsh') == '/bin/zsh':
        # OS X but Homebrew Zsh not installed
        if yesno('install newer Zsh version using Homebrew?'):
            subprocess.check_call(['brew', 'install', 'zsh'])
            needs_append = True
            with open('/etc/shells') as shells:
                for line in shells:
                    if line.strip() == '/usr/local/bin/zsh':
                        needs_append = False
                        break
            if needs_append:
                subprocess.check_output(['sudo', 'tee', '-a', '/etc/shells'], input=b'/usr/local/bin/zsh\n')
            print('[ ** ] Added to /etc/shells. You can now `chsh -s /usr/local/bin/zsh` and relog.')

bootstrap_zsh.requires('gitdir')

@bootstrap_zsh.test_installed
def bootstrap_syncbin_private():
    return (git_dir() / 'github.com' / 'zsh-users' / 'zsh-syntax-highlighting' / 'master').is_dir()

def bootstrap(*setups):
    for setup_name in setups:
        if setup_name not in BOOTSTRAP_SETUPS:
            print('[!!!!] Unknown setup for `syncbin bootstrap`: {!r}'.format(setup_name), file=sys.stderr)
            bootstrap_help(file=sys.stderr)
            sys.exit(1)
    for setup_name in setups:
        #TODO check requirements
        BOOTSTRAP_SETUPS[setup_name]()

def bootstrap_help(file=sys.stdout):
    print('[ ** ] Available setups:', file=file)
    setups = sorted(BOOTSTRAP_SETUPS.items())
    max_len = max(len(name) for name, setup in setups)
    for name, setup in setups:
        try:
            import blessings

            term = blessings.Terminal()
        except:
            status_sigil = {
                True: '✓',
                False: '✗',
                None: '?'
            }[setup.is_installed()]
        else:
            status_sigil = {
                True: term.bright_green('✓'),
                False: term.bright_red('✗'),
                None: term.bright_yellow('?')
            }[setup.is_installed()]
        print('{} {}{}  {}'.format(status_sigil, name, ' ' * (max_len - len(name)), '(undocumented)' if setup.__doc__ is None else setup.__doc__), file=file)
        #TODO more details

if __name__ == '__main__':
    try:
        arguments = docopt(__doc__, version='fenhl/syncbin {}'.format(version()))
    except NameError:
        arguments = {
            'bootstrap': True,
            '<setup>': ['python']
        }
    if arguments['bootstrap']:
        if len(arguments['<setup>']) == 0:
            bootstrap_help()
        else:
            bootstrap(*arguments['<setup>'])
    elif arguments['hasinet']:
        sys.exit(subprocess.call(['syncbin-hasinet']))
    elif arguments['install']:
        sys.exit(subprocess.call(['sh', str(git_dir() / 'github.com' / 'fenhl' / 'syncbin' / 'master' / 'config' / 'install.sh')]))
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
        if which('zsh') is None:
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
