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
import importlib
import pathlib
import os
import subprocess
import json
import platform
import shutil
import stat
import time

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

def get_os():
    result = subprocess.run(['uname', '-s'], stdout=subprocess.PIPE, encoding='utf-8', check=True).stdout[:-1]
    if result == 'Linux':
        if shutil.which('lsb_release') is not None:
            result = subprocess.run(['lsb_release', '-si'], stdout=subprocess.PIPE, encoding='utf-8', check=True).stdout[:-1]
        elif pathlib.Path('/etc/redhat-release').exists():
            with open('/etc/redhat-release') as redhat_release_f:
                result = redhat_release_f.read().split(' ')[0]
        elif pathlib.Path('/system/build.prop').exists():
            result = 'Android'
        else:
            raise RuntimeError('Could not get Linux distro')
    elif result == 'Darwin':
        result = 'macOS'
    elif result == 'MSYS_NT-10.0':
        result = 'Windows'
    else:
        raise RuntimeError('Unknown OS: {}'.format(result))
    return result

@contextlib.contextmanager
def lock(lock_name):
    path = pathlib.Path(f'/tmp/syncbin-startup-{lock_name}.lock').resolve()
    while True:
        try:
            path.mkdir()
        except FileExistsError:
            try:
                import psutil
            except ImportError:
                pass # don't check pid file if psutil is missing
            else:
                if (path / 'pid').exists():
                    with (path / 'pid').open() as pid_f:
                        pid = int(pid_f.read().strip())
                    if not psutil.pid_exists(pid):
                        with contextlib.suppress(FileNotFoundError): #TODO (Python 3.8) remove suppress context and use unlink(missing_ok=True) instead
                            (path / 'pid').unlink()
                        path.rmdir()
            time.sleep(1)
            continue
        break
    try:
        with (path / 'pid').open('w') as pid_f:
            print(os.getpid(), file=pid_f)
        yield path
    finally:
        with contextlib.suppress(FileNotFoundError): #TODO (Python 3.8) remove suppress context and use unlink(missing_ok=True) instead
            (path / 'pid').unlink()
        path.rmdir()

def py_dir():
    return pathlib.Path('/opt/py' if root() else '{}/py'.format(os.environ['HOME']))

def pypi_import(name, package=None):
    # just try importing the module first, in case it's already installed
    with contextlib.suppress(ImportError):
        return importlib.import_module(name)
    # import failed, try installing the package
    if package is None:
        package = name
    with contextlib.suppress(ImportError): # Debian doesn't have ensurepip but does have pip
        import ensurepip
        ensurepip.bootstrap(upgrade=True, user=True)
    subprocess.run([sys.executable or 'python3', '-m', 'pip', 'install' , '--quiet', '--user', package], check=True)
    return importlib.import_module(name)

def root():
    if getpass.getuser() == 'root':
        return True
    return subprocess.run(['sudo', '-n', 'true'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0

def version():
    try:
        with (git_dir() / 'github.com' / 'fenhl' / 'syncbin' / 'master' / 'version.txt').open() as version_file:
            return version_file.read().strip()
    except:
        return '0.0'

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
        f.apt_packages = set()
        f.dist_apt_packages = {}
        return f
    return inner_wrapper

@bootstrap_setup('brew')
def bootstrap_brew():
    """Installs various utilities for macOS using Homebrew"""
    try:
        subprocess.run(['brew', 'install', 'git', 'jq', 'libheif', 'ruby', 'terminal-notifier'], check=True)
    except subprocess.CalledProcessError:
        subprocess.run(['brew', 'link', '--overwrite', 'ruby'], check=True)
    subprocess.run(['brew', 'cask', 'install', 'bartender', 'bitbar', 'discord', 'firefox', 'qlmarkdown'], check=True)

@bootstrap_brew.test_installed
def bootstrap_brew():
    if shutil.which('brew') is None:
        return False
    return len(json.loads(subprocess.run(['brew', 'info', '--json=v1', 'terminal-notifier'], stdout=subprocess.PIPE, encoding='utf-8', check=True).stdout)[0]['installed']) > 0

@bootstrap_setup('debian-root')
def bootstrap_debian_root():
    """Essential setup for Debian systems with root access"""
    if getpass.getuser() == 'root':
        subprocess.run(['chmod', 'u+s', shutil.which('ping')], check=True)
    else:
        subprocess.run(['sudo', 'chmod', 'u+s', shutil.which('ping')], check=True)

bootstrap_debian_root.apt_packages = {
    'cmark', # for md
    'exiftool',
    'htop',
    'jq',
    'needrestart',
    'ntp',
    'ruby',
    'ruby-dev',
    'screen',
    'ssmtp', #TODO configure
    'unattended-upgrades' #TODO configure (unattended-upgrades config, call night-device-report)
}

# exa not available on Ubuntu for some reason
bootstrap_debian_root.dist_apt_packages['Debian'] = {'exa'}
bootstrap_debian_root.dist_apt_packages['Raspbian'] = {'exa'}

@bootstrap_debian_root.test_installed
def bootstrap_debian_root():
    if getpass.getuser() == 'root':
        try:
            subprocess.run(['systemctl', '-q', 'is-active', 'ntp'], stderr=subprocess.DEVNULL, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False
        else:
            return True
    else:
        # make sure sudo and systemctl work
        try:
            subprocess.run(['sudo', '-n', 'systemctl'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        except:
            return None
        # check if ntp (installed by this setup) is running
        try:
            subprocess.run(['sudo', '-n', 'systemctl', '-q', 'is-active', 'ntp'], stderr=subprocess.DEVNULL, check=True)
        except subprocess.CalledProcessError:
            return False
        else:
            return True

@bootstrap_setup('finder')
def bootstrap_finder():
    """Configure useful defaults for Finder on macOS"""
    print('[....] configuring Finder', end='\r', flush=True)
    subprocess.run(['launchctl', 'unload', '-w', '/System/Library/LaunchAgents/com.apple.rcd.plist'], check=True) #FROM https://www.howtogeek.com/274345/stop-itunes-from-launching-when-you-press-play-on-your-macs-keyboard/ # seems to work with SIP enabled now
    subprocess.run(['defaults', 'write', '-g', 'NSScrollViewRubberbanding', '-int', '0'], check=True)
    subprocess.run(['defaults', 'write', 'com.apple.finder', 'AppleShowAllFiles', '-bool', 'true'], check=True)
    subprocess.run(['defaults', 'write', 'com.apple.finder', '_FXShowPosixPathInTitle', '-bool', 'true'], check=True)
    print('[ ok ]')
    print('[....] restarting Finder', end='\r', flush=True)
    subprocess.run(['killall', 'Finder'], check=True)
    print('[ ok ]')
    print('[....] configuring Dock', end='\r', flush=True)
    subprocess.run(['defaults', 'write', 'com.apple.Dock', 'showhidden', '-bool', 'true'], check=True)
    print('[ ok ]')
    print('[....] restarting Dock', end='\r', flush=True)
    subprocess.run(['killall', 'Dock'], check=True)
    print('[ ok ]')

@bootstrap_finder.test_installed
def bootstrap_finder():
    try:
        #TODO check if Play key has been fixed
        return subprocess.run(['defaults', 'read', 'com.apple.finder', '_FXShowPosixPathInTitle'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True).stdout == b'1\n'
    except FileNotFoundError:
        return None
    except subprocess.CalledProcessError:
        return False

@bootstrap_setup('gitdir')
def bootstrap_gitdir():
    """Installs `gitdir` and configures `git`. Requires the `python` setup."""
    subprocess.run(['git', 'config', '--global', 'merge.conflictstyle', 'diff3'], check=True)
    gitdir_gitdir = git_dir(existing_only=False) / 'github.com' / 'fenhl' / 'gitdir'
    if not gitdir_gitdir.exists():
        gitdir_gitdir.mkdir(parents=True)
    if not (gitdir_gitdir / 'master').exists():
        subprocess.run(['git', 'clone', 'https://github.com/fenhl/gitdir.git', 'master'], cwd=str(git_dir() / 'github.com' / 'fenhl' / 'gitdir'), check=True)
    if not py_dir().exists():
        try:
            py_dir().mkdir()
        except PermissionError:
            subprocess.run(['sudo', 'mkdir', str(py_dir())], check=True)
    if not (py_dir() / 'gitdir').exists():
        try:
            (py_dir() / 'gitdir').symlink_to(gitdir_gitdir / 'master' / 'gitdir')
        except PermissionError:
            subprocess.run(['sudo', 'ln', '-s', str(gitdir_gitdir / 'master' / 'gitdir'), str(py_dir() / 'gitdir')], check=True)

@bootstrap_gitdir.test_installed
def bootstrap_gitdir():
    try:
        sys.path.append(str(py_dir()))
        import gitdir
    except ImportError:
        return False
    else:
        return True

@bootstrap_setup('keylayout')
def bootstrap_keylayout():
    if get_os() == 'macOS':
        repo = gitdir.host.by_name('github.com').repo('fenhl/german-and-wanya-for-apple-international-english.keylayout')
        repo.clone()
        if getpass.getuser() == 'root':
            shutil.copy(repo.branch_path() / 'German and Wanya for Apple International English.keylayout', '/Library/Keyboard Layouts')
        else:
            subprocess.run(['sudo', 'cp', repo.branch_path() / 'German and Wanya for Apple International English.keylayout', '/Library/Keyboard Layouts'], check=True)
    else:
        raise NotImplementedError(f"Don't know how to install the keyboard layout for {get_os()}")

bootstrap_keylayout.requires('gitdir')

@bootstrap_setup('macbook')
def bootstrap_macbook():
    """Installs `batcharge` for MacBooks."""
    bin_path = (pathlib.Path.home() / 'bin')
    if not bin_path.exists():
        bin_path.mkdir()
    batcharge = bin_path / 'batcharge'
    batcharge.symlink_to(git_dir() / 'fenhl.net' / 'syncbin-private' / 'master' / 'bin' / 'batcharge-macbook')

bootstrap_macbook.requires('syncbin-private')

@bootstrap_macbook.test_installed
def bootstrap_macbook():
    config_path = (pathlib.Path.home() / 'bin' / 'batcharge')
    if not config_path.is_symlink():
        return False
    return config_path.resolve() == (git_dir() / 'fenhl.net' / 'syncbin-private' / 'master' / 'python' / 'batcharge_macbook.py').resolve()

@bootstrap_setup('nginx')
def bootstrap_nginx():
    """Installs the nginx_ensite utility"""
    try:
        sys.path.append(str(py_dir()))
        import gitdir.host
    except ImportError:
        print('[ ** ] run `syncbin bootstrap gitdir`, then re-run `syncbin bootstrap nginx` to install packages from github')
    else:
        gitdir.host.by_name('github.com').clone('perusio/nginx_ensite')
        subprocess.run(['sudo', 'make', 'install'], cwd=str(gitdir.host.by_name('github.com').repo('perusio/nginx_ensite').branch_path()))

bootstrap_nginx.requires('gitdir')

@bootstrap_nginx.test_installed
def bootstrap_nginx():
    return shutil.which('nginx_ensite') is not None

@bootstrap_setup('no-battery')
def bootstrap_no_battery():
    """Installs `batcharge` for devices without batteries."""
    bin_path = (pathlib.Path.home() / 'bin')
    if not bin_path.exists():
        bin_path.mkdir()
    batcharge = bin_path / 'batcharge'
    with batcharge.open('w') as f:
        print('#!/bin/sh\n\nexit 0', file=f)
    batcharge.chmod(batcharge.stat().st_mode | stat.S_IEXEC)

@bootstrap_no_battery.test_installed
def bootstrap_no_battery():
    if not (pathlib.Path.home() / 'bin' / 'batcharge').exists():
        return False
    with (pathlib.Path.home() / 'bin' / 'batcharge').open() as batcharge_f:
        return batcharge_f.read() == '#!/bin/sh\n\nexit 0\n'

@bootstrap_setup('python')
def bootstrap_python():
    """Creates `/opt/py` and links Python modules."""
    try:
        sys.path.append(str(py_dir()))
        import gitdir.host
    except ImportError:
        print('[ ** ] run `syncbin bootstrap gitdir`, then re-run `syncbin bootstrap python` to install packages from github')
    else:
        gitdir.host.by_name('github.com').clone('fenhl/python-xdg-basedir')
        gitdir.host.by_name('github.com').clone('fenhl/python-class-key')
        gitdir.host.by_name('github.com').clone('fenhl/fancyio')
        gitdir.host.by_name('github.com').clone('fenhl/lazyjson')
        gitdir.host.by_name('github.com').clone('fenhl/python-timespec')
        if root() and getpass.getuser() != 'root':
            if not (py_dir() / 'basedir.py').exists():
                subprocess.run(['sudo', 'ln', '-s', str(git_dir() / 'github.com' / 'fenhl' / 'python-xdg-basedir' / 'master' / 'basedir'), str(py_dir() / 'basedir')], check=True)
            if not (py_dir() / 'class_key.py').exists():
                subprocess.run(['sudo', 'ln', '-s', str(git_dir() / 'github.com' / 'fenhl' / 'python-class-key' / 'master' / 'class_key.py'), str(py_dir() / 'class_key.py')], check=True)
            if not (py_dir() / 'fancyio.py').exists():
                subprocess.run(['sudo', 'ln', '-s', str(git_dir() / 'github.com' / 'fenhl' / 'fancyio' / 'master' / 'fancyio.py'), str(py_dir() / 'fancyio.py')], check=True)
            if not (py_dir() / 'lazyjson.py').exists():
                subprocess.run(['sudo', 'ln', '-s', str(git_dir() / 'github.com' / 'fenhl' / 'lazyjson' / 'master' / 'lazyjson'), str(py_dir() / 'lazyjson')], check=True)
            if not (py_dir() / 'timespec').exists():
                subprocess.run(['sudo', 'ln', '-s', str(git_dir() / 'github.com' / 'fenhl' / 'python-timespec' / 'master' / 'timespec'), str(py_dir() / 'timespec')], check=True)
        else:
            if not (py_dir() / 'basedir.py').exists():
                (py_dir() / 'basedir').symlink_to(git_dir() / 'github.com' / 'fenhl' / 'python-xdg-basedir' / 'master' / 'basedir')
            if not (py_dir() / 'basedir.py').exists():
                (py_dir() / 'class_key.py').symlink_to(git_dir() / 'github.com' / 'fenhl' / 'python-class-key' / 'master' / 'class_key.py')
            if not (py_dir() / 'fancyio.py').exists():
                (py_dir() / 'fancyio.py').symlink_to(git_dir() / 'github.com' / 'fenhl' / 'fancyio' / 'master' / 'fancyio.py')
            if not (py_dir() / 'lazyjson.py').exists():
                (py_dir() / 'lazyjson').symlink_to(git_dir() / 'github.com' / 'fenhl' / 'lazyjson' / 'master' / 'lazyjson')
            if not (py_dir() / 'timespec').exists():
                (py_dir() / 'timespec').symlink_to(git_dir() / 'github.com' / 'fenhl' / 'python-timespec' / 'master' / 'timespec')

bootstrap_python.requires('gitdir')

@bootstrap_python.test_installed
def bootstrap_python():
    try:
        sys.path.append(str(py_dir()))
        import basedir, fancyio, lazyjson, timespec
    except ImportError:
        return False
    else:
        return True

@bootstrap_setup('rust')
def bootstrap_rust():
    """Installs Rust via `rustup`."""
    #TODO install Rust via apt-get if on Debian ≥10
    subprocess.run('curl --proto \'=https\' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- --no-modify-path -y', shell=True, check=True)
    if shutil.which('exa') is None:
        subprocess.run(['cargo', 'install', 'cargo-update', 'exa'], check=True)
    subprocess.run(['cargo', 'install', '--git=https://github.com/fenhl/diskspace'], check=True)

bootstrap_rust.apt_packages = {
    'curl',
    'libssl-dev',
    'pkg-config'
}

@bootstrap_rust.test_installed
def bootstrap_rust():
    return shutil.which('rustup') is not None

@bootstrap_setup('ssh')
def bootstrap_ssh():
    """Copies the `syncbin` SSH config file, generates a public key if none exists, and optionally copies it onto mercredi."""
    config_path = (pathlib.Path.home() / '.ssh' / 'config')
    shutil.copy2(str(git_dir() / 'github.com' / 'fenhl' / 'syncbin' / 'master' / 'config' / 'ssh'), str(config_path))
    config_path.chmod(0o600) # http://serverfault.com/a/253314
    if platform.system() == 'Darwin' and shutil.which('ssh-copy-id') is None:
        subprocess.run(['brew', 'install', 'ssh-copy-id'], check=True)
    with open('/dev/zero', 'rb') as dev_zero:
        subprocess.run(['ssh-keygen', '-q', '-N', ''], stdin=dev_zero, stdout=subprocess.DEVNULL, check=True)
    if yesno('copy SSH pubkey onto mercredi?'):
        subprocess.run(['ssh-copy-id', 'mercredi'], check=True)

@bootstrap_ssh.test_installed
def bootstrap_ssh():
    config_path = (pathlib.Path.home() / '.ssh' / 'config')
    return subprocess.run(['diff', str(config_path), str(git_dir() / 'github.com' / 'fenhl' / 'syncbin' / 'master' / 'config' / 'ssh')], stdout=subprocess.DEVNULL).returncode == 0

@bootstrap_setup('sudo')
def bootstrap_sudo():
    """Configures passwordless `sudo`."""
    #TODO if Touch ID is supported, use instead: https://medium.com/@jalalazimi/how-to-enable-touch-id-for-sudo-on-macbook-pro-46272ac3e2df
    sudoers_d = pathlib.Path('/etc/sudoers.d')
    if not sudoers_d.exists():
        subprocess.run(['sudo', 'mkdir', '-p', str(sudoers_d)], check=True)
    print('[ ** ] For passwordless login, insert the following line into the opened document:')
    print('fenhl ALL=(ALL) NOPASSWD: ALL')
    input('[ ?? ] Press return to continue')
    subprocess.run(['sudo', 'nano', str(sudoers_d / 'fenhl')], check=True)

@bootstrap_sudo.test_installed
def bootstrap_sudo():
    return subprocess.run(['sudo', '-n', 'true'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0 #TODO remove false positive due to sudo mode, remove false negative due to Touch ID

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
    try:
        import syncbin_private
    except ImportError:
        return False
    else:
        return True

@bootstrap_setup('t')
def bootstrap_t():
    """Installs the Twitter CLI `t`."""
    import gitdir.host

    try:
        gitdir.host.by_name('github.com').clone('sferik/t')
    except PermissionError:
        sys.exit('[!!!!] Permission denied. Fix /opt/git permissions, then try again.')
    if root() and getpass.getuser() != 'root':
        subprocess.run(['sudo', 'gem', 'install', 't'], check=True)
    else:
        subprocess.run(['gem', 'install', 't'], check=True)
    subprocess.run(['t', 'authorize', '--display-uri'], check=True)

@bootstrap_t.test_installed
def bootstrap_t():
    return shutil.which('t') is not None

@bootstrap_setup('zsh')
def bootstrap_zsh():
    """Installs useful extensions for Zsh."""
    sys.path.append(str(py_dir()))
    import gitdir.host

    gitdir.host.by_name('github.com').clone('zsh-users/zsh-syntax-highlighting')
    gitdir.host.by_name('github.com').clone('robbyrussell/oh-my-zsh')
    if platform.system() == 'Darwin' and shutil.which('zsh') == '/bin/zsh':
        # macOS but Homebrew Zsh not installed
        if yesno('install newer Zsh version using Homebrew?'):
            subprocess.run(['brew', 'install', 'zsh'], check=True)
            needs_append = True
            with open('/etc/shells') as shells:
                for line in shells:
                    if line.strip() == '/usr/local/bin/zsh':
                        needs_append = False
                        break
            if needs_append:
                subprocess.run(['sudo', 'tee', '-a', '/etc/shells'], input=b'/usr/local/bin/zsh\n', stdout=subprocess.DEVNULL, check=True)
            print('[ ** ] Added to /etc/shells. You can now `chsh -s /usr/local/bin/zsh` and relog.')

bootstrap_zsh.requires('gitdir')

@bootstrap_zsh.test_installed
def bootstrap_zsh():
    return (git_dir() / 'github.com' / 'zsh-users' / 'zsh-syntax-highlighting' / 'master').is_dir()

if bootstrap_syncbin_private.is_installed():
    import syncbin_private

    if hasattr(syncbin_private, 'update_bootstrap_setups'):
        syncbin_private.update_bootstrap_setups(BOOTSTRAP_SETUPS)

def bootstrap(*setups):
    apt_packages = set()
    for setup_name in setups:
        apt_packages |= BOOTSTRAP_SETUPS[setup_name].dist_apt_packages.get(get_os(), set())
        if get_os() in ('Debian', 'Raspbian', 'Ubuntu'):
            apt_packages |= BOOTSTRAP_SETUPS[setup_name].apt_packages
    if apt_packages:
        subprocess.run(([] if getpass.getuser() == 'root' else ['sudo']) + ['apt-get', 'install', '-y'] + sorted(apt_packages), check=True)
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
        sys.exit(subprocess.run(['syncbin-hasinet']).returncode)
    elif arguments['install']:
        sys.exit(subprocess.run(['sh', str(git_dir() / 'github.com' / 'fenhl' / 'syncbin' / 'master' / 'config' / 'install.sh')]).returncode)
    elif arguments['startup']:
        sys.exit(subprocess.run(['syncbin-startup'] + (['--ignore-lock'] if arguments['--ignore-lock'] else []) + (['--no-internet-test'] if arguments['--no-internet-test'] else [])).returncode)
    elif arguments['update']:
        mode = None
        if arguments['public']:
            mode = 'public'
        elif arguments['private']:
            mode = 'private'
        elif arguments['hooks']:
            mode = 'hooks'
        if shutil.which('zsh') is None:
            # Zsh missing, use bash
            if arguments['<old>'] is None:
                sys.exit(subprocess.run(['bash', 'syncbin-update'] + ([] if mode is None else [mode])).returncode)
            else:
                sys.exit(subprocess.run(['bash', 'syncbin-update'] + ([] if mode is None else [mode]) + [arguments['<old>'], arguments['<new>']]).returncode)
        else:
            # use Zsh
            if arguments['<old>'] is None:
                sys.exit(subprocess.run(['syncbin-update'] + ([] if mode is None else [mode])).returncode)
            else:
                sys.exit(subprocess.run(['syncbin-update'] + ([] if mode is None else [mode]) + [arguments['<old>'], arguments['<new>']]).returncode)
    else:
        raise NotImplementedError('unknown subcommand')
