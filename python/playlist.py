#!/usr/bin/env python3

"""Playlist-manipulating mpc wrapper script.

Usage:
  playlist
  playlist addfrom <path>
  playlist -h | --help
  playlist --version

Options:
  -h, --help  Print this message and exit.
  --version   Print version info and exit.
"""

import sys

from docopt import docopt
import os
import pathlib
import subprocess
import syncbin

__version__ = syncbin.__version__

mpd_root = pathlib.Path(os.environ.get('MPD_ROOT', '/Users/fenhl/Music'))

if __name__ == '__main__':
    arguments = docopt(__doc__, version='playlist from fenhl/syncbin ' + __version__)
    if arguments['addfrom']:
        path = pathlib.Path(arguments['<path>'])
        if (mpd_root / path).is_dir():
            sys.exit(subprocess.call(['mpc', 'add', str(path)]))
        else:
            found = False
            for file in sorted((mpd_root / path).parent.iterdir()):
                if file.name.startswith(path.name):
                    found = True
                if found:
                    subprocess.call(['mpc', 'add', str(file.relative_to(mpd_root))])
    else:
        sys.exit(subprocess.call(['mpc', 'playlist', "--format=%position% %file%"]))
