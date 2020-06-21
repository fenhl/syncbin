#!/usr/bin/env python3

"""Playlist-manipulating mpc wrapper script.

Usage:
  playlist [options]
  playlist [options] add <path>
  playlist [options] add-from <path>
  playlist [options] add-random <path>
  playlist lyrics [<path>]
  playlist [options] pause-after-current [<num-tracks>]
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

import pathlib
import sys

sys.path += ['/opt/py', str(pathlib.Path.home() / 'py')]

import contextlib
import os
import random
import re
import socket
import subprocess

import blessings # PyPI: blessings
import docopt # PyPI: docopt
import mpd # PyPI: python-mpd2

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
    if not arguments.get('--filenames'):
        with contextlib.suppress(KeyError):
            return '{} — {}'.format(song['artist'], song['title'])
    return song['file']

if __name__ == '__main__':
    arguments = docopt.docopt(__doc__, version='playlist from fenhl/syncbin ' + __version__)
    if arguments['add']:
        # add the given path to the playlist in alphabetical order
        path = pathlib.Path(arguments['<path>'])
        if (MPD_ROOT / path).is_dir():
            track_iterator = (MPD_ROOT / path).iterdir()
        else:
            track_iterator = iter([MPD_ROOT / path])
        amount = float('inf') if arguments['--all'] or arguments['--number'] == 'all' else (float('inf') if arguments['--number'] is None else int(arguments['--number']))
        i = 0
        for f in sorted(track_iterator):
            if i >= amount:
                break
            subprocess.run(['mpc', 'add', str(f.relative_to(MPD_ROOT))], check=True)
            i += 0
    if arguments['add-from']:
        # add files from the given path's parent, starting with the given path, to the playlist in alphabetical order
        path = pathlib.Path(arguments['<path>'])
        track_iterator = (MPD_ROOT / path).parent.iterdir()
        amount = float('inf') if arguments['--all'] or arguments['--number'] == 'all' else (float('inf') if arguments['--number'] is None else int(arguments['--number']))
        found = False
        i = 0
        for f in sorted(track_iterator):
            if f.name.startswith(path.name):
                found = True
            if found:
                if i >= amount:
                    break
                subprocess.run(['mpc', 'add', str(f.relative_to(MPD_ROOT))], check=True)
                i += 1
    elif arguments['add-random']:
        tracks = subprocess.run(['mpc', 'ls', arguments['<path>']], stdout=subprocess.PIPE, encoding='utf-8', check=True).splitlines()
        random.shuffle(tracks)
        amount = float('inf') if arguments['--all'] or arguments['--number'] == 'all' else (1 if arguments['--number'] is None else int(arguments['--number']))
        for i, track in enumerate(tracks):
            if i >= amount:
                break
            exit_status = subprocess.run(['mpc', 'add', track]).returncode
            if exit_status != 0:
                sys.exit(exit_status)
    elif arguments['lyrics']:
        sys.exit(subprocess.run(['eyeD3', arguments['<path>'] or client().playlistid()[0]['file']]).returncode) #TODO only display lyrics, not other ID3 tags
    elif arguments['pause-after-current']:
        num_tracks = int(arguments['<num-tracks>']) if arguments['<num-tracks>'] else 1
        c = client(idle_timeout=1)
        for i in range(num_tracks):
            song = c.currentsong()
            print('[....] {}'.format(format_song(song, arguments)), end='\r[....]', flush=True)
            if i == num_tracks - 1:
                c.single(1)
            try:
                while True:
                    progress = min(4, int(5 * float(c.status()['elapsed']) / float(song['time'])))
                    print('\r[{}{}]'.format('=' * progress, '.' * (4 - progress)), end='', flush=True)
                    try:
                        c.idle('player')
                    except socket.timeout:
                        c = client(idle_timeout=1)
                    if c.currentsong().get('id') != song['id']:
                        break
            except KeyboardInterrupt:
                print('\r[ ^C ] {}'.format(format_song(song, arguments)), flush=True)
                client().single(0)
                sys.exit(1)
            print('\r[ ok ]', flush=True)
        c.single(0)
    elif arguments['repeat-current-once']:
        current = subprocess.run(['mpc', 'current', '--format=%file%'], stdout=subprocess.PIPE, encoding='utf-8', check=True)[:-1].decode('utf-8')
        sys.exit(subprocess.run(['mpc', 'insert', current]).returncode)
    else:
        c = client()
        for song in c.playlistid():
            if int(song['pos']) > 9999:
                print('[ ** ]', 'playlist truncated')
                break
            print('[{: >4}] {}'.format(int(song['pos']), format_song(song, arguments)))
