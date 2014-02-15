# -*- coding: utf-8 -*-

import sys

_syncbin_python_version_string = str(sys.version_info.major) + '.' + str(sys.version_info.minor)

sys.ps1 = '[' + _syncbin_python_version_string + '>] '
sys.ps2 = '[' + _syncbin_python_version_string + '…] '
