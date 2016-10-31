#!/usr/bin/env python3

"""Playlist-manipulating mpc wrapper script.

Usage:
  playlist
  playlist [options] add-from <path>
  playlist [options] add-random <path>
  playlist pause-after-current
  playlist repeat-current-once
  playlist -h | --help
  playlist --version

Options:
  -a, --all              Add all items in the directory. Overrides `--number'.
  -h, --help             Print this message and exit.
  -l, --filenames        Print tracks as filenames instead of the default “artist — title format.
  -n, --number=<number>  Add this many items maximum. Set <number> to `all' to add all items in the directory. Defaults to `all' for `add-random', and `1' for `add-from'.
  --version              Print version info and exit.
"""

import sys

sys.path.append('/opt/py')

import blessings
import docopt
import mpd
import os
import pathlib
import random
import re
import socket
import subprocess
import syncbin

__version__ = syncbin.__version__

MPD_ROOT = pathlib.Path(os.environ.get('MPD_ROOT', '/Users/fenhl/Music'))

def client(host=None, port=6600, *, password=None, idle_timeout=None):
    if host is None:
        password, host = os.environ['MPD_HOST'].split('@')
    c = mpd.MPDClient()
    c.connect(host, port)
    if password is not None:
        c.password(password)
    if idle_timeout is not None:
        c.idletimeout = idle_timeout
    return c

def format_song(song, arguments={}):
    if arguments.get('--filenames'):
        return song['file']
    else:
        return '{} — {}'.format(song['artist'], song['title'])

if __name__ == '__main__':
    arguments = docopt.docopt(__doc__, version='playlist from fenhl/syncbin ' + __version__)
    if arguments['add-from']:
        path = pathlib.Path(arguments['<path>'])
        if (mpd_root / path).is_dir():
            found = True
            dir_iterator = (mpd_root / path).iterdir()
        else:
            found = False
            dir_iterator = (mpd_root / path).parent.iterdir()
        amount = float('inf') if arguments['--all'] or arguments['--number'] == 'all' else (float('inf') if arguments['--number'] is None else int(arguments['--number']))
        i = 0
        for f in sorted(dir_iterator):
            if f.name.startswith(path.name):
                found = True
            if found:
                if i >= amount:
                    break
                subprocess.call(['mpc', 'add', str(f.relative_to(mpd_root))])
                i += 1
    elif arguments['add-random']:
        tracks = subprocess.check_output(['mpc', 'ls', arguments['<path>']]).decode('utf-8').strip().split('\n')
        random.shuffle(tracks)
        amount = float('inf') if arguments['--all'] or arguments['--number'] == 'all' else (1 if arguments['--number'] is None else int(arguments['--number']))
        for i, track in enumerate(tracks):
            if i >= amount:
                break
            exit_status = subprocess.call(['mpc', 'add', track])
            if exit_status != 0:
                sys.exit(exit_status)
    elif arguments['pause-after-current']:
        c = client(idle_timeout=1)
        song = c.currentsong()
        print('[....] {}'.format(format_song(song, arguments)), end='\r[....]', flush=True)
        c.single(1)
        while True:
            progress = int(5 * float(c.status()['elapsed']) / float(song['time']))
            print('\r[{}{}]'.format('=' * progress, '.' * (4 - progress)), end='', flush=True)
            try:
                c.idle('player')
            except socket.timeout:
                c = client(idle_timeout=1)
            if c.currentsong()['id'] != song['id']:
                break
        c.single(0)
        print('\r[ ok ]', flush=True)
    elif arguments['repeat-current-once']:
        current = subprocess.check_output(['mpc', 'current', '--format=%file%'])[:-1].decode('utf-8')
        sys.exit(subprocess.call(['mpc', 'insert', current]))
    else:
        mpc_playlist = subprocess.Popen(['mpc', 'playlist'] + (['--format=%position% %file%'] if arguments['--filenames'] else []), stdout=subprocess.PIPE)
        for byte_line in mpc_playlist.stdout:
            line = byte_line.decode('utf-8')
            match = re.match('([0-9]+) (.*)\n', line)
            if match:
                index = int(match.group(1))
                if index > 9999:
                    print('[ ** ]', 'playlist truncated')
                    mpc_playlist.communicate()
                    sys.exit(mpc_playlist.returncode)
                print('[{: >4}] {}'.format(index, match.group(2)))
            else:
                print('[ !! ]', line)
        sys.exit(mpc_playlist.wait())
