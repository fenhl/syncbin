#!/usr/bin/env python3

import pathlib
import sys

sys.path += ['/opt/py', str(pathlib.Path.home() / 'py')]

import basedir
import shlex
import subprocess

def info_beamer_invocation():
    custom_cmd = pathlib.Path.home() / '.config' / 'fenhl' / 'info-beamer'
    if custom_cmd.exists():
        return [str(custom_cmd)]
    #TODO support info-beamer-open-source (see ~/.config/fenhl/info-beamer @ familiepc)
    return ['sudo', '-E', str(pathlib.Path.home() / 'info-beamer-pi' / 'info-beamer')]

def run_node(node, *args, check=True, **kwargs):
    configured_nodes = basedir.config_dirs('fenhl/syncbin.json').json(base={}).get('info-beamer', {}).get('nodes', {})
    if node in configured_nodes:
        return subprocess.run(configured_nodes[node] + list(args), check=check, **kwargs)
    else:
        node_path = pathlib.Path(node).expanduser().resolve()
        return subprocess.run(info_beamer_invocation() + [str(node_path)] + list(args), check=check, **kwargs)

if __name__ == '__main__':
    if sys.argv[1] == '--list':
        for node_name, invocation in basedir.config_dirs('fenhl/syncbin.json').json(base={}).get('info-beamer', {}).get('nodes', {}).items():
            print('{}: {}'.format(node_name, ' '.join(shlex.quote(arg) for arg in invocation)))
    else:
        sys.exit(run_node(*sys.argv[1:], check=False).returncode)
