#!/bin/zsh

function cwd-exists {
    python3 <<EOF                                                                                                                                                             [rust: ][exit: 1]
import pathlib, sys
try:
    pathlib.Path().resolve()
except:
    sys.exit(1)
EOF
}

if ! cwd-exists; then
    echo '[cwd: does not exist]'
fi
