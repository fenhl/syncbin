#!/usr/bin/env python3 -i

"""Edit JSON files using Python's interactive mode.

Usage:
  jpy [FILE...]
  jpy -h | --help

Options:
  -h, --help  Print this message and exit.

"""

import sys

sys.path.append('/opt/py')

import builtins
import docopt
import json
import lazyjson
import os
import subprocess

files = []
f = files
objects = files
obj = files

# some JSON aliases
true = True
false = False
null = None

def help():
    print(__doc__)

def load(filename):
    path = os.path.abspath(os.path.expanduser(filename))
    with open(path, 'a'):
        os.utime(path, None) # touch the file
    try:
        ret = lazyjson.File(path)
        ret.value()
    except ValueError:
        print('[ !! ] Could not decode JSON from file ' + str(filename))
        return
    files.append(ret)
    return ret

touch = load

def l(json_node):
    if isinstance(json_node, lazyjson.Node):
        json_node = json_node.value()
    print(json.dumps(json_node, sort_keys=True, indent=4, separators=(',', ': ')))

def ll(json_node):
    if isinstance(json_node, lazyjson.Node):
        json_node = json_node.value()
    popen = subprocess.Popen('less', stdin=subprocess.PIPE, shell=True)
    popen.communicate(input=json.dumps(json_node, sort_keys=True, indent=4, separators=(',', ': ')).encode('utf-8'))

def keys(json_node):
    if not isinstance(json_node, dict) and not isinstance(json_node, lazyjson.Dict):
        print('[ !! ] not an object')
        return
    key_list = sorted(list(json_node.keys()))
    if len(key_list) == 0:
        print('[ ** ] empty')
    else:
        for key in key_list:
            if json_node[key] is None:
                value_type = '[null] '
            elif isinstance(json_node[key], dict) or isinstance(json_node[key], lazyjson.Dict):
                value_type = '[obj ] '
            elif isinstance(json_node[key], list) or isinstance(json_node[key], lazyjson.List):
                value_type = '[arr ] '
            elif isinstance(json_node[key], str):
                value_type = '[str ] '
            elif isinstance(json_node[key], bool):
                value_type = '[bool] '
            elif isinstance(json_node[key], int) or isinstance(json_node[key], float):
                value_type = '[num ] '
            else:
                value_type = '[unkn] '
            print(value_type + key)

def quit():
    sys.exit()

q = quit

if __name__ == '__main__':
    def displayhook(value):
        if value is None:
            return
        # Set '_' to None to avoid recursion
        builtins._ = None
        if isinstance(value, lazyjson.Node):
            text = json.dumps(value.value(), sort_keys=True, indent=4, separators=(',', ': '))
        else:
            text = repr(value)
        try:
            sys.stdout.write(text)
        except UnicodeEncodeError:
            bytes = text.encode(sys.stdout.encoding, 'backslashreplace')
            if hasattr(sys.stdout, 'buffer'):
                sys.stdout.buffer.write(bytes)
            else:
                text = bytes.decode(sys.stdout.encoding, 'strict')
                sys.stdout.write(text)
        sys.stdout.write("\n")
        builtins._ = value
    
    sys.ps1 = '[jpy>] '
    sys.ps2 = '[jpy…] '
    sys.displayhook = displayhook
    arguments = docopt.docopt(__doc__)
    for filename in arguments['FILE']:
        o = load(filename)
