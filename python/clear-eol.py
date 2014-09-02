#!/usr/bin/env python3

import sys

sys.path.append('/opt/py')

import blessings

if __name__ == '__main__':
    terminal = blessings.Terminal()
    print(terminal.clear_eol, end='')
    sys.stdout.flush()
