#!/usr/bin/env python3

"""

Usage:
  edit <command_or_file>
  edit -h | --help
  edit --version

Options:
  -h, --help  Print this message and exit
  --version   Print version info and exit
"""

import sys

from docopt import docopt
import os
import subprocess
import syncbin

__version__ = syncbin.__version__

def resolve(command_or_file):
    if command_or_file.startswith('~'):
        return os.path.expanduser(command_or_file)
    elif '/' in command_or_file:
        return os.path.abspath(command_or_file)
    else:
        return subprocess.check_output(['which', command_or_file]).decode('utf-8').splitlines()[0]

def run(path):
    return subprocess.call([os.environ.get('VISUAL', os.environ.get('EDITOR', 'nano')), path])

if __name__ == '__main__':
    arguments = docopt(__doc__, version='edit from fenhl/syncbin ' + __version__)
    try:
        cmd_or_file = resolve(arguments['<command_or_file>'])
    except subprocess.CalledProcessError:
        sys.exit('[!!!!] edit: command ' + repr(arguments['<command_or_file>']) + ' not found')
    sys.exit(run(cmd_or_file))
