#!/bin/zsh

if where vcgencmd &> /dev/null; then
    temperature="$(vcgencmd measure_temp)"
    if echo "$temperature" | python3 -c $'import re, sys; sys.exit(0 if float(re.search("=(.*)\'", sys.stdin.read()).group(1)) >= 80.0 else 1)'; then
        echo "$temperature" | python3 -c $'import re, sys; print("[temperature: {}]".format(re.search("=(.*)\'", sys.stdin.read()).group(1)))'
    fi
fi
