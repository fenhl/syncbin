#!/usr/bin/env python3

import sys

sys.path.append('/opt/py')

import blessings

if __name__ == '__main__':
    terminal = blessings.Terminal()
    for _ in range(int(sys.argv[1]) if len(sys.argv) > 1 else 1):
        print(terminal.move_up, end='')
        sys.stdout.flush()
