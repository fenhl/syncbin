#!/bin/zsh

if ! [[ -d "$(pwd -P)" ]]; then
    echo '[cwd: does not exist]'
fi
