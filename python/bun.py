#!/usr/bin/env python3

"""Print Python reprs of input chars

Usage:
  bun [options] [<string>...]
  bun -h | --help
  bun --version

Options:
  -h, --help                               Print this message and exit.
  -n, --number-of-characters=<characters>  How many characters to wait for, if no string is specified [Default: 1].
  --version                                Print version info and exit.
"""

import sys

from docopt import docopt
import syncbin
import termios
import tty

__version__ = syncbin.__version__

def getch_loop():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        while True:
            yield sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

if __name__ == '__main__':
    arguments = docopt(__doc__, version='bun from fenhl/syncbin ' + __version__)
    if len(arguments['<string>']):
        for string_arg in arguments['<string>']:
            print(repr(string_arg))
    else:
        getch = getch_loop()
        for _ in range(int(arguments['--number-of-characters'])):
            print(repr(next(getch)), end='\r\n')
        del getch
