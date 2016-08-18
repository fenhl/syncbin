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

sys.path.append('/opt/py')

import os
import pathlib
import platform
import stat
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

def which(cmd):
    try:
        return subprocess.check_output(['which', cmd]).decode('utf-8')[:-1]
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

@bootstrap_setup('debian-root')
def bootstrap_debian_root():
    """Essential setup for Debian systems with root access"""
    subprocess.check_call(['sudo', 'apt-get', 'install', 'needrestart', 'ntp', 'ruby-dev'])
    subprocess.check_call(['sudo', 'chmod', 'u+s', which('ping')])

@bootstrap_debian_root.test_installed
def bootstrap_debian_root():
    try:
        subprocess.check_call(['sudo', '-n', 'true'])
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
    gitdir_gitdir = GITDIR / 'github.com' / 'fenhl' / 'gitdir'
    if not gitdir_gitdir.exists():
        gitdir_gitdir.mkdir(parents=True)
    if not (gitdir_gitdir / 'master').exists():
        subprocess.check_call(['git', 'clone', 'https://github.com/fenhl/gitdir.git', 'master'], cwd=str(GITDIR / 'github.com' / 'fenhl' / 'gitdir'))
    if not pathlib.Path('/opt/py/gitdir').exists():
        if not pathlib.Path('/opt/py').exists():
            sys.exit('[!!!!] run `syncbin bootstrap python` first')
        try:
            pathlib.Path('/opt/py/gitdir').symlink_to(gitdir_gitdir / 'master' / 'gitdir')
        except PermissionError:
            subprocess.check_call(['sudo', 'ln', '-s', str(gitdir_gitdir / 'master' / 'gitdir'), '/opt/py/gitdir'])

@bootstrap_gitdir.test_installed
def bootstrap_gitdir():
    try:
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
    batcharge.symlink_to(GITDIR / 'fenhl.net' / 'syncbin-private' / 'master' / 'bin' / 'batcharge-macbook')

bootstrap_macbook.requires('syncbin-private')

@bootstrap_macbook.test_installed
def bootstrap_macbook():
    if not hasattr(pathlib.Path, 'home'): # Python 3.4 and below
        return None
    config_path = (pathlib.Path.home() / 'bin' / 'batcharge')
    if not config_path.is_symlink():
        return False
    return config_path.resolve() == GITDIR / 'fenhl.net' / 'syncbin-private' / 'master' / 'bin' / 'batcharge-macbook'

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
    subprocess.check_call(['pip3', 'install', 'blessings', 'docopt', 'requests'])
    if not pathlib.Path('/opt/py').exists():
        subprocess.check_call(['sudo', 'mkdir', '/opt/py'])
    try:
        import gitdir.host
    except ImportError:
        print('[ ** ] run `syncbin bootstrap gitdir`, then re-run `syncbin bootstrap python` to install essentials from github')
    else:
        gitdir.host.by_name('github.com').clone('fenhl/python-xdg-basedir')
        subprocess.check_output(['sudo', 'ln', '-s', str(GITDIR / 'github.com' / 'fenhl' / 'python-xdg-basedir' / 'master' / 'basedir.py'), '/opt/py/basedir.py'])
        gitdir.host.by_name('github.com').clone('fenhl/lazyjson')
        subprocess.check_output(['sudo', 'ln', '-s', str(GITDIR / 'github.com' / 'fenhl' / 'lazyjson' / 'master' / 'lazyjson.py'), '/opt/py/lazyjson.py'])

@bootstrap_python.test_installed
def bootstrap_python():
    try:
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
    #    sys.exit('[ !! ] missing requests, run `syncbin bootstrap python` first')
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
    config_path.symlink_to(GITDIR / 'github.com' / 'fenhl' / 'syncbin' / 'master' / 'config' / 'ssh')
    if platform.system() == 'Darwin' and which('ssh-copy-id') is None:
        subprocess.check_call(['brew', 'install', 'ssh-copy-id'])

@bootstrap_ssh.test_installed
def bootstrap_ssh():
    if not hasattr(pathlib.Path, 'home'): # Python 3.4 and below
        return None
    config_path = (pathlib.Path.home() / '.ssh' / 'config')
    if not config_path.is_symlink():
        return False
    return config_path.resolve() == GITDIR / 'github.com' / 'fenhl' / 'syncbin' / 'master' / 'config' / 'ssh'

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
        subprocess.check_call(['sudo', '-n', 'true'])
    except subprocess.CalledProcessError:
        return False
    else:
        return True

@bootstrap_setup('syncbin-private')
def bootstrap_syncbin_private():
    """Installs the private `syncbin` extensions."""
    import gitdir.host

    try:
        gitdir.host.by_name('fenhl.net').clone('syncbin-private')
    except PermissionError:
        sys.exit('[ !! ] Permission denied. Fix /opt/git permissions, then try again.')

bootstrap_syncbin_private.requires('gitdir')

@bootstrap_syncbin_private.test_installed
def bootstrap_syncbin_private():
    return (GITDIR / 'fenhl.net' / 'syncbin-private' / 'master').is_dir()

@bootstrap_setup('zsh')
def bootstrap_zsh():
    """Installs useful extensions for Zsh."""
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
    return (GITDIR / 'github.com' / 'zsh-users' / 'zsh-syntax-highlighting' / 'master').is_dir()

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
        status_sigil = {
            True: '✓',
            False: '✗',
            None: '?'
        }[setup.is_installed()]
        print('{} {}{}  {}'.format(status_sigil, name, ' ' * (max_len - len(name)), '(undocumented)' if setup.__doc__ is None else setup.__doc__), file=file)
        #TODO more details

if __name__ == '__main__':
    try:
        arguments = docopt(__doc__, version='fenhl/syncbin ' + __version__)
    except NameError:
        arguments = {
            'bootstrap': True,
            '<setup>': 'python'
        }
    if arguments['bootstrap']:
        if len(arguments['<setup>']) == 0:
            bootstrap_help()
        else:
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
