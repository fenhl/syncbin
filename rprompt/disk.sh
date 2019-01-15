#!/bin/zsh

if which diskspace &> /dev/null; then
    diskspace --zsh 2> /dev/null
else
    echo '[disk: unknown]'
fi
