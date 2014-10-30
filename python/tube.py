#!/usr/bin/env python3

"""A Python wrapper around youtube-dl for downloading and watching YouTube videos.

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

__version__ = '2.2.0'

import sys

from datetime import datetime
import os.path
import subprocess

def delete(video_id):
    if video_id is None:
        sys.exit('[!!!!] No video specified')
    else:
        os.remove(os.path.expanduser('~/Movies/tube/' + video_id + '.mp4'))

def download(video_id):
    if video_id is None:
        sys.exit('[!!!!] No video specified')
    else:
        subprocess.check_call(['youtube-dl', '--id', 'https://youtube.com/watch?v=' + video_id], stdout=subprocess.DEVNULL, cwd=os.path.expanduser('~/Movies/tube'))

def list_videos():
    subprocess.call(['ls', '-hlF', os.path.expanduser('~/Movies/tube')])

def open_videos_dir():
    subprocess.call(['open', os.path.expanduser('~/Movies/tube')])

def print_timestamp():
    print('[ ** ] ' + datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))

def print_version():
    print('[ ** ] tube ' + __version__ + ' by Fenhl')

def watch(video_id, block=True):
    if video_id is None:
        print('[!!!!] No video specified', file=sys.stderr)
    else:
        subprocess.check_call(['open'] + (['-nW'] if block else []) + ['--', video_id + '.mp4'], cwd=os.path.expanduser('~/Movies/tube'))

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
                    print('[!!!!] Syntax error: missing video ID', file=sys.stderr)
                    sys.exit(1)
                else:
                    video_id = arguments.pop(0)
            elif argument.startswith('--video='):
                video_id = argument[len('--video='):]
            elif argument == '--watch':
                watch(video_id)
            elif argument == '--watch-in-background':
                watch(video_id, block=False)
            else:
                sys.exit('[!!!!] No such action: ' + argument)
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
                        sys.exit('[!!!!] Syntax error: missing video ID')
                elif letter == 'w':
                    watch(video_id)
                elif letter == 'W':
                    watch(video_id, block=False)
                else:
                    sys.exit('[!!!!] No such action: ' + letter)
        else:
            video_id = argument
