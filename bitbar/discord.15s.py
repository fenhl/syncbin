#!/usr/local/bin/python3

import sys

sys.path.append('/opt/git/github.com/fenhl/syncbin/master/python')

import decimal
import warnings

import syncbin
warnings.filterwarnings('ignore')
requests = syncbin.pypi_import('requests')

import basedir # https://github.com/fenhl/python-xdg-basedir

# the Discord logo, used to represent Discord (https://discord.com/)
DISCORD_LOGO = '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'

config = basedir.config_dirs('bitbar/plugins/discord.json').json()
guilds = config.get('guilds', [])
responses = []

for guild in guilds:
    if 'username' in guild or 'password' in guild:
        auth = (guild['username'], guild['password'])
    else:
        auth = None
    try:
        response = requests.get(guild['apiUrl'], auth=auth, timeout=30.05)
        response.raise_for_status()
    except requests.RequestException as e:
        responses.append(e)
    else:
        responses.append(response.json(parse_float=decimal.Decimal))

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
                        print(f'{member["username"].replace("|", "¦")}#{member["discriminator"]}')
