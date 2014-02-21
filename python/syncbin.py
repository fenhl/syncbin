import os

try:
    with open(os.path.join(os.environ.get('HUB', '/opt/hub'), 'fenhl', 'syncbin', 'version.txt')) as version_file:
        __version__ = version_file.read().strip()
except:
    __version__ = '0.0'
