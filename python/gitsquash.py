#!/usr/bin/env python3

"""Squash the last n commits together.

Usage:
  git-squash [options] <n>
  git-squash -h | --help
  git-squash --version

Options:
  -h, --help               Print this message and exit.
  -m, --message=<message>  Set the commit message. Defaults to the original commit message of the oldest squashed commit.
  --version                Print version info and exit.
"""

import sys

from docopt import docopt
import subprocess
import syncbin

__version__ = syncbin.version()

if __name__ == '__main__':
    arguments = docopt(__doc__, version='git squash from fenhl/syncbin ' + __version__)
    n = int(arguments['<n>'])
    commit_message = arguments['--message'] or subprocess.check_output(['git', 'log', '-1', '--pretty=format:%s', 'HEAD~{}'.format(n - 1)])
    if n < 2:
        sys.exit('[!!!!] must squash at least 2 commits')
    subprocess.check_call(['git', 'reset', '--soft', 'HEAD~{}'.format(n)])
    sys.exit(subprocess.call(['git', 'commit', '-m', commit_message]))
