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

if cwd-exists; then
    if ! where rustup &> /dev/null; then
        if where rustup &> /dev/null; then
            echo "[rust: rustup not installed]"
        else
            exit 0 # Rust not installed
        fi
    fi
    if rustup override list | grep 'no overrides' &> /dev/null; then
        exit 0 # no overrides
    fi
    rustup_override=$(
        rustup override list |
        grep 'override toolchain' |
        rustup override list |
        awk '{
            res=$2
            split(res, resArr, "-")
            print resArr[1]
        }'
    )
    echo "[rust: ${rustup_override}]"
fi
