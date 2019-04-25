#!/usr/bin/env PYTHONIOENCODING=UTF-8 /usr/local/bin/python3

# BitBar plugin showing which followed channels are live. Based on https://getbitbar.com/plugins/Web/Twitch/livestreamer-now-playing.5m.js

import sys

sys.path.append('/opt/py')

import collections
import datetime
import pathlib
import re
import subprocess
import traceback

warnings.filterwarnings('ignore')
import basedir
import requests

CACHE = basedir.data_dirs('bitbar/plugin-cache/twitch.json').lazy_json(writeable_only=True, default={})
DEFER_DELTAS = {
    '20m': datetime.timedelta(minutes=20),
    '1h': datetime.timedelta(hours=1),
    '4h': datetime.timedelta(hours=4),
    '1d': datetime.timedelta(days=1),
    '1w': datetime.timedelta(days=7)
}
QUALITY_PREFERENCES = [
    '720p60',
    '720p',
    '480p',
    'high'
]
SCRIPT_PATH = pathlib.Path(__file__).resolve()
STREAMLINK_PATH = pathlib.Path('/usr/local/bin/streamlink')
TWITCH_LOGO = 'iVBORw0KGgoAAAANSUhEUgAAACQAAAAkCAYAAADhAJiYAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAACXBIWXMAABYlAAAWJQFJUiTwAAABWWlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNS40LjAiPgogICA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPgogICAgICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgICAgICAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyI+CiAgICAgICAgIDx0aWZmOk9yaWVudGF0aW9uPjE8L3RpZmY6T3JpZW50YXRpb24+CiAgICAgIDwvcmRmOkRlc2NyaXB0aW9uPgogICA8L3JkZjpSREY+CjwveDp4bXBtZXRhPgpMwidZAAACGUlEQVRYCe1WzSsFURT3beUjslF6pUjYKNnIwl/ATjaeBf+AUkr2spDYSGEnWSDFgu2zkWLHnyAWUqJ8/07vzOvOnTNz77w7puSd+rlzfuezc2beVVZWkj82gfKIfudg64ywJ2HKIcmWbaJvOP42jvVmKnSC9WwInzR9ryes0gnWZxT+FM/riu76WIkEm0A9QBswSg881FUtGiPiO9xxjcD7I61sVsvfqOmuajUS0JREkRpqED1TIqWGXlOqLZaRGhIdQ8gx8DfAgWBfZduCYAulwr6y0ADN0Aq9C6jTeFJ7AbLF+nF1ndALVYY85A/f30fWnnysQXFtyJA+vrnUkGlmrhNq4gIdQqEMc/TiW4vrV3aGSrUAXQW6LIHoBi40Q+T95drQJYoRJNmTSHAfgNdU4P8x15WF1IykJ2H1Vt2ie6bd0DQa2Abocv0CVgCf2KzMG68vsAiFmtnguHecA8A164XDZkLer3EhqIiHKcR4zVC42AwZbCY0Dr9+ctZkHnqOObqz1oAa1tWD1jPIxCdOyhWYDNvFYwcsrcmECY6mZt4s/CkfXbixxbahDDLTLU/vg6l5+tT7AKNI71CbMSr/hYzA7wqwWTs1Q75GCfwwIWIYaA+JzIIfAmgieuwROIIu5yBudTIpna4DaT2HSRWQVhaVu1kw7oMbFfhUKLqf1AntJl3V5oVUa55AeWaCGltWjaXnfzmBH5k9h5BGwGKzAAAAAElFTkSuQmCC'

def read_access_token():
    data = basedir.config_dirs('streamlink/config').read()
    for line in data.split('\n'):
        if line.startswith('twitch-oauth-token='):
            return line[line.index('=') + 1:]

ACCESS_TOKEN = read_access_token()

def get_data(access_token=ACCESS_TOKEN):
    response = requests.get('https://api.twitch.tv/kraken/streams/followed?stream_type=live', headers={'Authorization': f'OAuth {access_token}'})
    response.raise_for_status()
    return response.json()

def output_for_stream(stream):
    channel = stream['channel']
    time_live = datetime.datetime.utcnow() - datetime.datetime.strptime(stream['created_at'], '%Y-%m-%dT%H:%M:%SZ')
    if time_live >= datetime.timedelta(hours=1):
        time_live = '{}h {}m'.format(time_live // datetime.timedelta(hours=1), (time_live % datetime.timedelta(hours=1)) // datetime.timedelta(minutes=1))
    else:
        time_live = '{}m'.format(time_live // datetime.timedelta(minutes=1))
    yield channel['display_name']
    yield '--{}'.format(channel['status'].replace('|', '¦').replace('\n', ' '))
    try:
        for line in subprocess.run([str(STREAMLINK_PATH), channel['url']], check=True, stdout=subprocess.PIPE, encoding='utf-8').stdout.splitlines():
            if line.startswith('Available streams: '):
                available_streams = set(re.sub(' \\(.+?\\)', '', line[line.index(': ') + 2:]).split(', '))
                for quality in QUALITY_PREFERENCES:
                    if quality in available_streams:
                        break
                else:
                    continue
                yield f'--📺 live for {time_live}|terminal=false bash={STREAMLINK_PATH} param1={channel["url"]} param2={quality}'
                yield f'--📺 {quality}|alternate=true'
                break
        else:
            yield '--📺 available streams: {}|'.format(', '.join(available_streams))
    except subprocess.CalledProcessError:
        yield '--📺 no streams available'
    yield f'--👥 {stream["viewers"]} viewers|href=https://twitch.tv/{channel["name"]}/chat?popout='
    yield '-----'
    yield f'--Hide This Stream|terminal=false bash=/Users/fenhl/bin/bitbar-twitch param1=hide-stream param2={channel["_id"]} refresh=true'
    yield f'--Hide This Game|terminal=false bash=/Users/fenhl/bin/bitbar-twitch param1=hide-game param2={channel["_id"]} param3="{stream["game"]}" refresh=true'

def handle_response(response):
    online_streams = [
        stream
        for stream in response['streams']
        if not stream['is_playlist']
    ]
    CACHE['hiddenStreams'] = [
        channel_id
        for channel_id in CACHE.get('hiddenStreams', [])
        if any(stream['channel']['_id'] == channel_id for stream in online_streams)
    ]
    online_streams = [
        stream
        for stream in online_streams
        if stream['stream_type'] != 'rerun'
            and stream['channel']['_id'] not in CACHE.get('hiddenStreams', [])
            and stream['game'] not in CACHE.get('hiddenGames', {}).get(str(stream['channel']['_id']), [])
    ]
    streams_by_game = collections.defaultdict(list)
    for stream in online_streams:
        streams_by_game[stream['channel']['game']].append(stream)
    if len(online_streams) == 0:
        return
    yield f'{len(online_streams)}|templateImage={TWITCH_LOGO}'
    for game, streams in sorted(streams_by_game.items()):
        yield '---'
        yield f'{game}|'
        for stream in streams:
            yield from output_for_stream(stream)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        if 'deferred' in CACHE and datetime.datetime.strptime(CACHE['deferred'].value(), '%Y-%m-%d %H:%M:%S') >= datetime.datetime.utcnow():
            sys.exit() # deferred
        if ACCESS_TOKEN is None:
            print(f'💔|templateImage={TWITCH_LOGO}')
            print('---')
            print(f'Click to authenticate streamlink | terminal=false bash={STREAMLINK_PATH} param1=--twitch-oauth-authenticate')
            sys.exit()
        try:
            print('\n'.join(handle_response(get_data())))
            print('---')
            print('defer')
            for delta_str in DEFER_DELTAS:
                print(f'--{delta_str}|bash={SCRIPT_PATH} param1=defer param2={delta_str} terminal=false refresh=true')
        except Exception as e:
            print(f'?|templateImage={TWITCH_LOGO}')
            print('---')
            print(f'{e.__class__.__name__}: {e}')
            traceback.print_exc(file=sys.stdout)
    elif sys.argv[1] == 'defer':
        CACHE['deferred'] = f'{datetime.datetime.utcnow() + DEFER_DELTAS[sys.argv[2]]:%Y-%m-%d %H:%M:%S}'
    else:
        sys.exit('Usage: bitbar-twitch [defer <delta>]')
