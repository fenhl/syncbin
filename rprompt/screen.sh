#!/bin/zsh

if [[ -n "$STY" ]]; then
    echo "[screen: ${STY#*.}]"
fi
