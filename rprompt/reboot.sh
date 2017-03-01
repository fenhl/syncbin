#!/bin/zsh

if which jq &> /dev/null; then
    if [[ "$(cat /opt/dev/reboot.json | jq '.schedule')" != "null" ]]; then
        echo "[reboot: $(cat /opt/dev/reboot.json | jq -r '.schedule')]"
    fi
else
    echo '[reboot: unknown (jq not found)]'
fi
