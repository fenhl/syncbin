#!/usr/bin/env python3

import sys

import re
import subprocess

def format_space(num_bytes):
    if num_bytes >= 2 ** 50:
        return str(num_bytes // (2 ** 50)) + 'PB'
    if num_bytes >= 2 ** 40:
        return str(num_bytes // (2 ** 40)) + 'TB'
    if num_bytes >= 2 ** 30:
        return str(num_bytes // (2 ** 30)) + 'GB'
    if num_bytes >= 2 ** 20:
        return str(num_bytes // (2 ** 20)) + 'MB'
    if num_bytes >= 2 ** 10:
        return str(num_bytes // (2 ** 20)) + 'KB'
    return str(int(num_bytes))

def parse_space(space_string):
    space_string = str(space_string)
    match = re.match('([0-9.]+)([PTGMKB])', space_string)
    if match:
        amount, unit = match.group(1, 2)
        return {
            'P': 2 ** 50,
            'T': 2 ** 40,
            'G': 2 ** 30,
            'M': 2 ** 20,
            'K': 2 ** 10,
            'B': 1
        }[unit] * int(amount)
    return int(space_string)

ONE_GIG = 2 ** 30

try:
    output = subprocess.check_output(['df', '-hl', '/'], stderr=subprocess.STDOUT).decode('utf-8')
    space = parse_space(output.splitlines()[1].split()[3])
except:
    print('[disk: error]')
    sys.exit(1)

if '--zsh' not in sys.argv or space < ONE_GIG:
    if '--bytes' in sys.argv:
        print(str(space))
    else:
        print('[disk: ' + format_space(space) + ']')
