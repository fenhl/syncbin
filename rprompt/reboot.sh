#!/bin/zsh

if which jq &> /dev/null; then
    if [[ -a /opt/dev/reboot.json ]]; then
        if [[ -f /opt/dev/reboot.json ]]; then
            if [[ -r /opt/dev/reboot.json ]]; then
                if [[ "$(cat /opt/dev/reboot.json | jq '.schedule')" != "null" ]]; then
                    echo "[reboot: $(cat /opt/dev/reboot.json | jq -r '.schedule')]"
                fi
            else
                echo '[reboot: can'"'"'t read /opt/dev/reboot.json]'
            fi
        else
            echo '[reboot: /opt/dev/reboot.json is not a regular file]'
        fi
    fi
else
    echo '[reboot: jq not found]'
fi
