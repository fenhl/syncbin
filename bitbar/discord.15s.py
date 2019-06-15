#!/usr/local/bin/python3

import sys

sys.path.append('/opt/git/github.com/fenhl/syncbin/master/python')

import warnings

warnings.filterwarnings('ignore')
import basedir
import requests

# the Discord logo, used to represent Discord (https://discordapp.com/)
DISCORD_LOGO = 'iVBORw0KGgoAAAANSUhEUgAAACYAAAAmCAYAAACoPemuAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAACXBIWXMAABYlAAAWJQFJUiTwAAABWWlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNS40LjAiPgogICA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPgogICAgICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgICAgICAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyI+CiAgICAgICAgIDx0aWZmOk9yaWVudGF0aW9uPjE8L3RpZmY6T3JpZW50YXRpb24+CiAgICAgIDwvcmRmOkRlc2NyaXB0aW9uPgogICA8L3JkZjpSREY+CjwveDp4bXBtZXRhPgpMwidZAAABvklEQVRYCe1WiXGDMBDEqSAlUIJLoASXQAnuQOnA6YB04BJSgkuwO0gJya3gmJUiJCHC4MxwM/I97J7Wh8Cuqt32CewTyJ7AUZAmG91jwVnF7tL1e1ivBTvciH8u4P+iaEMIU4OwqywVmvJGieJb4n1SPTvE6HVDCGkp13qJ/5I+MHjl1yjkGkh3WUaWNvhrX1NvCV07uKnNIGALc7S8bKEgZ09HpRC2mpZqHfU87cT+hbCTznNDj9eUtfGeSrb1+RokVVZTya38kA5v2iXDA/vIwE1CUi9QfWtzg06SKR7jNJ7Ccl2x1uf89jkESrgpxwRxQsaE4gujQwC/xniOfRxywwAvDuH9WlVyxrx91kn1qYTilCnWx01x5+K572HOxG7MHOLxvRO4FipNfYkQ1tb8exzLG2Fg4SmN4XCtk4X/cyYDy70E3m/CxWeIk4f/3Upf5+ORatsIIDYl8GPX517DEYDFjkKPkM9OVmyDZkRW1TmBDfW5Et8k+C1hbYhCqCnXIMq3oxSwGVY3+Ea8bycpcK9Q3PokzVPkiwILPKYWEqO1JqdnSCDOxFJTEeybJU3rJeSdu09gn8CMCfwATTVPuywMjbAAAAAASUVORK5CYII='

config = basedir.config_dirs('bitbar/plugins/discord.json').json()
guilds = config.get('guilds', [])
responses = []

for guild in guilds:
    if 'username' in guild or 'password' in guild:
        auth = (guild['username'], guild['password'])
    else:
        auth = None
    try:
        response = requests.get(guild['apiUrl'], auth=auth)
        response.raise_for_status()
    except requests.RequestException as e:
        responses.append(e)
    else:
        responses.append(response.json())

total = sum(
    (
        float('inf')
        if isinstance(response, Exception) else
        sum(
            len(channel['members'])
            for channel in response['channels']
            if channel.get('snowflake') not in config.get('ignoredChannels', [])
        )
    )
    for response in responses
)

if total > 0:
    print(f'{"?" if total == float("inf") else total}|templateImage={DISCORD_LOGO}')
    for guild, response in zip(guilds, responses):
        if isinstance(response, Exception):
            print('---')
            print(f'{response.__class__.__name__} for {guild["name"]}: {response}')
        else:
            for channel in response['channels']:
                if len(channel['members']) > 0 and channel.get('snowflake') not in config.get('ignoredChannels', []):
                    print('---')
                    print(f'{guild["name"]}#{channel["name"]}')
                    for member in channel['members']:
                        print(f'{member["username"]}#{member["discriminator"]}')
