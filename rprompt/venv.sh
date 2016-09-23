#!/bin/zsh

if [[ -z "$VIRTUAL_ENV" ]]; then
    exit 0 # no venv active
else
    echo "[venv: $VIRTUAL_ENV]"
fi
