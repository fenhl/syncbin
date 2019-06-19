#!/usr/bin/env python3

import pathlib
import sys

sys.path += ['/opt/py', str(pathlib.Path.home() / 'py')]

import blessings

if __name__ == '__main__':
    terminal = blessings.Terminal()
    for _ in range(int(sys.argv[1]) if len(sys.argv) > 1 else 1):
        print(terminal.move_up, end='')
        sys.stdout.flush()
