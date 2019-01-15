#!/bin/zsh

if [[ -d "$(pwd -P)" ]]; then
    if which rust &> /dev/null; then
        rust rprompt 2> /dev/null
    else
        echo '[rust: unknown]'
    fi
fi
