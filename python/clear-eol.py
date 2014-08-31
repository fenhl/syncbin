#!/usr/bin/env python3

import blessings

if __name__ == '__main__':
    terminal = blessings.Terminal()
    print(terminal.clear_eol, end='', flush=True)

