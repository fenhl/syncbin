#!/usr/local/bin/python3

import sys

sys.path.append('/opt/git/github.com/fenhl/syncbin/master/python')

import basedir
import diskspace
import shutil

volumes = basedir.config_dirs('fenhl/syncbin.json').json().get('diskspace', {}).get('volumes', ['/'])
volumes_data = {
    volume: {'usage': shutil.disk_usage('/')}
    for volume in volumes
}

for volume, volume_data in volumes_data.items():
    volume_data['total'] = diskspace.Bytes(volume_data['usage'].total)
    volume_data['available'] = diskspace.Bytes(volume_data['usage'].free)

if any(volume_data['available'] < 5 * diskspace.ONE_GIG or volume_data['available'] / volume_data['total'] < 0.05 for volume_data in volumes_data.values()):
    print('low disk space') #TODO icon
    print('---')
    for volume in volumes:
        volume_data = volumes_data[volume]
        print('{}: {}% ({})'.format(volume, int(100 * volume_data['available'] / volume_data['total']), volume_data['available']))
    print('---')
    print('Open DaisyDisk|bash=/usr/bin/open param1=-a param2=DaisyDisk terminal=false')
