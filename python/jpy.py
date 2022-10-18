#!/usr/bin/env python3 -i

"""Edit JSON files using Python's interactive mode.

Usage:
  jpy [FILE...]
  jpy -h | --help

Options:
  -h, --help  Print this message and exit.

"""

import pathlib
import sys

sys.path += ['/opt/py', str(pathlib.Path.home() / 'py')]

import builtins
import decimal
import docopt
import json
import lazyjson
import os
import requests
import subprocess
import syncbin

__version__ = syncbin.__version__

files = []
f = files
objects = files
obj = files

# some JSON aliases
true = True
false = False
null = None

class DecimalEncoder(json.JSONEncoder): #FROM http://stackoverflow.com/a/3885198/667338
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o) # do not use str as that would enclose the value in quotes
        return super().default(o)

def load(filename):
    try:
        requests.get(filename)
    except requests.exceptions.MissingSchema:
        path = os.path.abspath(os.path.expanduser(filename))
        with open(path, 'a'):
            os.utime(path, None) # touch the file
        ret = lazyjson.File(path)
    else:
        ret = lazyjson.HTTPFile(filename)
    try:
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
    print(json.dumps(json_node, sort_keys=True, indent=4, separators=(',', ': '), cls=DecimalEncoder))

def ll(json_node):
    if isinstance(json_node, lazyjson.Node):
        json_node = json_node.value()
    popen = subprocess.Popen('less', stdin=subprocess.PIPE, shell=True)
    popen.communicate(input=json.dumps(json_node, sort_keys=True, indent=4, separators=(',', ': '), cls=DecimalEncoder).encode('utf-8'))

def keys(json_node):
    if isinstance(json_node, lazyjson.Node):
        key_list = [subnode.key_path[-1] for subnode in json_node]
    elif isinstance(json_node, dict):
        key_list = sorted(list(json_node.keys()))
    else:
        print('[ !! ] not an object')
        return
    if len(key_list) == 0:
        print('[ ** ] empty')
    else:
        for key in key_list:
            print('[{}] {}'.format({
                type(None): 'null',
                dict: 'obj ',
                list: 'arr ',
                str: 'str ',
                bool: 'bool',
                int: 'num ',
                float: 'num '
            }.get(val_type(json_node, key), 'unkn'), key))

def quit():
    sys.exit()

q = quit

def val_type(json_node, key):
    if isinstance(json_node, lazyjson.Node):
        return type(json_node[key].value())
    else:
        return type(json_node[key])

if __name__ == '__main__':
    def displayhook(value):
        if value is None:
            return
        # Set '_' to None to avoid recursion
        builtins._ = None
        if isinstance(value, lazyjson.Node):
            text = json.dumps(value.value(), sort_keys=True, indent=4, separators=(',', ': '), cls=DecimalEncoder)
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

    sys.ps1 = 'jpy> '
    sys.ps2 = 'jpy… '
    sys.displayhook = displayhook
    arguments = docopt.docopt(__doc__)
    for filename in arguments['FILE']:
        o = load(filename)
