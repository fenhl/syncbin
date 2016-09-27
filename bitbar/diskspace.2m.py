#!/usr/local/bin/python3

import sys

sys.path.append('/opt/git/github.com/fenhl/syncbin/master/python')

import diskspace
import shutil

usage = shutil.disk_usage('/')
total = diskspace.Bytes(usage.total)
available = diskspace.Bytes(usage.free)

if available < 5 * diskspace.ONE_GIG or available / total < 0.05:
    print('disk: {}% ({})'.format(int(100 * available / total), available))
