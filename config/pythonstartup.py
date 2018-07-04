# -*- coding: utf-8 -*-

import sys

import asyncio
import code
import collections.abc

_syncbin_python_version_string = str(sys.version_info.major) + '.' + str(sys.version_info.minor)

sys.ps1 = '[' + _syncbin_python_version_string + '>] '
sys.ps2 = '[' + _syncbin_python_version_string + '…] '

def namespace(initial=None):
    if initial is None:
        initial = {'__name__': '__console__', '__doc__': None}
    code.InteractiveConsole(locals=initial).interact('')
    return {k: v for k, v in initial.items() if not k.startswith('__')}

def sync(coro):
    def sync_iter(aiter):
        if hasattr(aiter, '__aiter__'):
            aiter = aiter.__aiter__()
        while True:
            try:
                yield sync(aiter.__anext__())
            except StopAsyncIteration:
                break

    if isinstance(coro, collections.abc.AsyncIterable):
        return sync_iter(coro)
    else:
        return asyncio.get_event_loop().run_until_complete(coro)
