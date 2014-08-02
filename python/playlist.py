#!/usr/bin/env python3

"""Playlist-manipulating mpc wrapper script.

Usage:
  playlist
  playlist add-from <path>
  playlist add-random <path>
  playlist -h | --help
  playlist --version

Options:
  -h, --help  Print this message and exit.
  --version   Print version info and exit.
"""

import sys

sys.path.append('/opt/py')

from docopt import docopt
import os
import pathlib
import random
import subprocess
import syncbin

__version__ = syncbin.__version__

mpd_root = pathlib.Path(os.environ.get('MPD_ROOT', '/Users/fenhl/Music'))

if __name__ == '__main__':
    arguments = docopt(__doc__, version='playlist from fenhl/syncbin ' + __version__)
    if arguments['add-from']:
        path = pathlib.Path(arguments['<path>'])
        if (mpd_root / path).is_dir():
            found = True
            dir_iterator = (mpd_root / path).iterdir()
        else:
            found = False
            dir_iterator = (mpd_root / path).parent.iterdir()
        for file in sorted(dir_iterator):
            if file.name.startswith(path.name):
                found = True
            if found:
                subprocess.call(['mpc', 'add', str(file.relative_to(mpd_root))])
    elif arguments['add-random']:
        sys.exit(subprocess.call(['mpc', 'add', random.choice(subprocess.check_output(['mpc', 'ls', arguments['<path>']]).decode('utf-8').strip().split('\n'))]))
    else:
        sys.exit(subprocess.call(['mpc', 'playlist', "--format=%position% %file%"]))
