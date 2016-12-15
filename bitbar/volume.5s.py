#!/usr/local/bin/python3

import subprocess

muted = subprocess.check_output(['osascript', '-e', 'output muted of (get volume settings)']).decode('utf-8') == 'true\n'
volume = int(subprocess.check_output(['osascript', '-e', 'output volume of (get volume settings)']).decode('utf-8'))

if muted:
    print('muted')
elif volume < 6:
    print('volume low')
elif volume > 13:
    print('volume high')
