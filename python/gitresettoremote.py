#!/usr/bin/env python3

"""Reset current git repository's state to be exactly like the remote.

Usage:
  git-reset-to-remote [options]
  git-reset-to-remote -h | --help
  git-reset-to-remote --version

Options:
  -h, --help              Print this message and exit.
  --branch=<branch_name>  The branch to reset to. Defaults to the current branch.
  --remote=<remote_name>  The remote to reset to [Default: origin].
  --version               Print version info and exit.
"""

import sys

from docopt import docopt
import subprocess
import syncbin

__version__ = syncbin.__version__

if __name__ == '__main__':
    arguments = docopt(__doc__, version='git reset-to-remote from fenhl/syncbin ' + __version__)
    if arguments['--branch']:
        branch = arguments['--branch']
    else:
        branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode('utf-8')[:-1]
    subprocess.check_call(['git', 'fetch', arguments['--remote']])
    sys.exit(subprocess.call(['git', 'reset', '--hard', arguments['--remote'] + '/' + branch]))
