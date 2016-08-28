#!/usr/bin/env python3

"""Edit a file.

Usage:
  edit [options] <command_or_file>
  edit -h | --help
  edit --version

Options:
  -c, --chocolat     Use Chocolat as the editor. Equivalent to `--editor=choc'.
  -h, --help         Print this message and exit.
  --editor=<editor>  The program with which to edit the file. Defaults to the value of the `VISUAL' or `EDITOR' environment variable, or `nano' if neither are set.
  --version          Print version info and exit.
"""

import sys

from docopt import docopt
import os
import subprocess
import syncbin

__version__ = syncbin.version()

def path(command_or_file):
    import pathlib
    if command_or_file.startswith('~'):
        path_string = os.path.expanduser(command_or_file)
    elif '/' in command_or_file:
        path_string = command_or_file
    else:
        path_string = subprocess.check_output(['which', command_or_file]).decode('utf-8').splitlines()[0]
    return pathlib.Path(path_string).resolve()

def resolve(command_or_file):
    if command_or_file.startswith('~'):
        return os.path.expanduser(command_or_file)
    elif '/' in command_or_file:
        return os.path.abspath(command_or_file)
    else:
        return subprocess.check_output(['which', command_or_file]).decode('utf-8').splitlines()[0]

def run(path, editor=None):
    if editor is None:
        editor = os.environ.get('VISUAL', os.environ.get('EDITOR', 'nano'))
    return subprocess.call([editor, str(path)])

if __name__ == '__main__':
    arguments = docopt(__doc__, version='edit from fenhl/syncbin ' + __version__)
    try:
        try:
            cmd_or_file = path(arguments['<command_or_file>'])
        except ImportError:
            cmd_or_file = resolve(arguments['<command_or_file>'])
    except subprocess.CalledProcessError:
        sys.exit('[!!!!] edit: command ' + repr(arguments['<command_or_file>']) + ' not found')
    if arguments['--chocolat']:
        editor = 'choc'
    elif arguments['--editor']:
        editor = arguments['--editor']
    else:
        editor = None
    sys.exit(run(cmd_or_file, editor=editor))
