#!/usr/bin/env python3

"""Batch-convert .m4a files to .mp3 using `ffmpeg`

Usage:
  m4a2mp3 [options] (<src>.m4a [<dst>.mp3])...
  m4a2mp3 [options] <directory>
  m4a2mp3 -h | --help

Options:
  -h, --help         Print this message and exit.
  --delete           Delete original files after converting.
"""

import sys

import pathlib
import subprocess

def convert(src_path, dest_path, delete=False):
    subprocess.check_call([
        'ffmpeg',
        '-loglevel',
        'error',
        '-i',
        str(src_path),
        '-acodec',
        'libmp3lame',
        '-ab',
        '320k',
        str(dest_path)
    ])
    if delete:
        src_path.unlink()

if __name__ == '__main__':
    delete = False
    conversions = {}
    src_path = None
    for argument in sys.argv[1:]:
        if argument.startswith('-'):
            if argument in ('-h', '--help'):
                print(__doc__)
            elif argument == '--delete':
                delete = True
            else:
                sys.exit('[!!!!] unknown option: {}'.format(argument))
        else:
            arg_path = pathlib.Path(argument)
            if arg_path.suffix == '':
                if not arg_path.is_dir():
                    sys.exit('[!!!!] unknown file type for {!r}'.format(argument))
                if src_path is not None:
                    conversions[src_path] = src_path.parent / '{}.mp3'.format(src_path.stem)
                conversions.update({path: path.parent / '{}.mp3'.format(path.stem) for path in arg_path.iterdir() if path.suffix == '.m4a'})
                src_path = None
            elif arg_path.suffix == '.m4a':
                if src_path is not None:
                    conversions[src_path] = src_path.parent / '{}.mp3'.format(src_path.stem)
                src_path = arg_path
            elif arg_path.suffix == '.mp3':
                if src_path is None:
                    sys.exit('[!!!!] missing source path for {!r}'.format(argument))
                conversions[src_path] = arg_path
                src_path = None
            else:
                sys.exit('[!!!!] unsupported file extension {!r}'.format(arg_path.suffix))
    if src_path is not None:
        conversions[src_path] = src_path.parent / '{}.mp3'.format(src_path.stem)
    for src_path, dest_path in conversions.items():
        convert(src_path, dest_path, delete)
