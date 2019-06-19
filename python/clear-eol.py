#!/usr/bin/env python3

import pathlib
import sys

sys.path += ['/opt/py', str(pathlib.Path.home() / 'py')]

import blessings

if __name__ == '__main__':
    terminal = blessings.Terminal()
    print(terminal.clear_eol, end='')
    sys.stdout.flush()
