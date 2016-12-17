#!/usr/local/bin/python3

import subprocess

MUTED = '' #TODO
LOW = '' #TODO
HIGH = '' #TODO

muted = subprocess.check_output(['osascript', '-e', 'output muted of (get volume settings)']).decode('utf-8') == 'true\n'
volume = int(subprocess.check_output(['osascript', '-e', 'output volume of (get volume settings)']).decode('utf-8'))

if muted:
    print('|templateImage={}'.format(MUTED))
elif volume < 6:
    print('|templateImage={}'.format(LOW))
elif volume > 13:
    print('|templateImage={}'.format(HIGH))
