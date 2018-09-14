#!/usr/bin/env python3

import sys

sys.path.append('/opt/py')

import basedir
import pathlib
import subprocess

def run_node(node, *args, check=True, **kwargs):
    configured_nodes = basedir.config_dirs('fenhl/info-beamer.json').json(base={}).get('nodes', {})
    if node in configured_nodes:
        return subprocess.run(configured_nodes[node] + list(args), check=check, **kwargs)
    else:
        node_path = pathlib.Path(node).expanduser().resolve()
        return subprocess.run(['sudo', '-E', '/home/fenhl/info-beamer-pi/info-beamer', str(node_path)] + list(args), check=check, **kwargs)

if __name__ == '__main__':
    sys.exit(run_node(*sys.argv[1:], check=False).returncode)
