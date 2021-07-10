#!/usr/bin/env python3

"""A convenience wrapper around youtube-dl for downloading and watching YouTube videos.

Usage:
  tube [options]

Options are read one by one, each performing an action as described below.

Options:
  -D, --delete               Delete the video.
  -V, --version              Print version info.
  -d, --download             Download the video from YouTube.
  -h, --help                 Print this message.
  -l, --list                 List all downloaded or partially downloaded videos.
  -o, --open                 Open the videos directory using Finder.
  -t, --timestamp            Print a timestamp.
  -v, --video=<video-id>     Use this video for all following actions. If a command-line argument does not start with a hyphen-minus, it is also interpreted as a video id.
  -w, --watch                Open the video. This action blocks until the video is closed again.
  -W, --watch-in-background  Open the video. This action does not block and does not open a new instance of the video player app.
"""

__version__ = '2.2.1'

import sys

import datetime
import pathlib
import subprocess

PATH = pathlib.Path.home() / 'Movies' / 'tube'

def delete(video_id):
    if video_id is None:
        sys.exit('tube: no video specified')
    else:
        (PATH / f'{video_id}.mp4').unlink()

def download(video_id):
    if video_id is None:
        sys.exit('tube: no video specified')
    else:
        PATH.mkdir(parents=True, exist_ok=True)
        subprocess.run(['youtube-dl', '--id', f'https://youtube.com/watch?v={video_id}'], stdout=subprocess.DEVNULL, cwd=PATH, check=True)

def list_videos():
    subprocess.run(['ls', '-hlF', str(PATH)], check=True)

def open_videos_dir():
    subprocess.run(['open', str(PATH)], check=True)

def print_timestamp():
    print(f'{datetime.datetime.utcnow():%Y-%m-%d %H:%M:%S}')

def print_version():
    print(f'tube {__version__} by Fenhl')

def watch(video_id, block=True):
    if video_id is None:
        print('tube: no video specified', file=sys.stderr)
    else:
        subprocess.run(['open'] + (['-nW'] if block else []) + ['--', video_id + '.mp4'], cwd=PATH, check=True)

if __name__ == '__main__':
    arguments = sys.argv[1:]
    video_id = None
    while len(arguments) > 0:
        argument = arguments.pop(0)
        if argument.startswith('--'):
            if argument == '--delete':
                delete(video_id)
            elif argument == '--download':
                download(video_id)
            elif argument == '--help':
                print(__doc__)
            elif argument == '--list':
                list_videos()
            elif argument == '--open':
                open_videos_dir()
            elif argument == '--timestamp':
                print_timestamp()
            elif argument == '--version':
                print_version()
            elif argument == '--video':
                if len(arguments) == 0:
                    sys.exit('tube: missing video ID')
                else:
                    video_id = arguments.pop(0)
            elif argument.startswith('--video='):
                video_id = argument[len('--video='):]
            elif argument == '--watch':
                watch(video_id)
            elif argument == '--watch-in-background':
                watch(video_id, block=False)
            else:
                sys.exit(f'tube: no such action: {argument}')
        elif argument.startswith('-'):
            letters = argument[1:]
            while len(letters) > 0:
                letter = letters[0]
                letters = letters[1:]
                if letter == 'D':
                    delete(video_id)
                elif letter == 'V':
                    print_version()
                elif letter == 'd':
                    download(video_id)
                elif letter == 'h':
                    print(__doc__)
                elif letter == 'l':
                    list_videos()
                elif letter == 'o':
                    open_videos_dir()
                elif letter == 't':
                    print_timestamp()
                elif letter == 'v':
                    if len(letters):
                        video_id = letters
                        break
                    elif len(arguments):
                        video_id = arguments.pop(0)
                    else:
                        sys.exit('tube: missing video ID')
                elif letter == 'w':
                    watch(video_id)
                elif letter == 'W':
                    watch(video_id, block=False)
                else:
                    sys.exit(f'tube: no such action: {letter}')
        else:
            video_id = argument
