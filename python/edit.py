#!/usr/bin/env python3

"""Edit a file.

Usage:
  edit [options] <command_or_file>
  edit -h | --help
  edit --version

Options:
  -a, --atom         Use Atom as the editor. Equivalent to `--editor=atom`.
  -c, --chocolat     Use Chocolat as the editor. Equivalent to `--editor=choc'.
  -h, --help         Print this message and exit.
  --editor=<editor>  The program with which to edit the file. Defaults to the value of the `VISUAL' or `EDITOR' environment variable, or `nano' if neither are set.
  --version          Print version info and exit.
"""

import sys

import docopt
import gitdir.host
import os
import pathlib
import subprocess
import syncbin

__version__ = syncbin.__version__

def path(command_or_file):
    if command_or_file.startswith('~'):
        return pathlib.Path(os.path.expanduser(command_or_file)).resolve()
    if '/' in command_or_file:
        return pathlib.Path(command_or_file).resolve()
    path = pathlib.Path(subprocess.check_output(['which', command_or_file]).decode('utf-8').splitlines()[0]).resolve()
    try:
        repo, path_kind = gitdir.host.Repo.lookup(path)
    except LookupError:
        return path
    else:
        if path_kind == 'master':
            return repo.stage_path.resolve()

def run(path, editor=None):
    if editor is None:
        editor = os.environ.get('VISUAL', os.environ.get('EDITOR', 'nano'))
    return subprocess.call([editor, str(path)])

if __name__ == '__main__':
    arguments = docopt.docopt(__doc__, version='edit from fenhl/syncbin ' + __version__)
    try:
        cmd_or_file = path(arguments['<command_or_file>'])
    except subprocess.CalledProcessError:
        sys.exit('[!!!!] edit: command ' + repr(arguments['<command_or_file>']) + ' not found')
    if arguments['--atom']:
        editor = 'atom'
    elif arguments['--chocolat']:
        editor = 'choc'
    elif arguments['--editor']:
        editor = arguments['--editor']
    else:
        editor = None
    sys.exit(run(cmd_or_file, editor=editor))
