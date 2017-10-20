#!/bin/zsh

if where vcgencmd &> /dev/null; then
    is_under_voltage=$(($(vcgencmd get_throttled | pcregrep -o '0x[0-9A-Fa-f]+') & 0x01))
    if [[ $is_under_voltage == 1 ]]; then
        echo '[pi: under-voltage]'
    fi
fi
