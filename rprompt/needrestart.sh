#!/bin/zsh

if which needrestart &> /dev/null && sudo -n true &> /dev/null; then
    # https://github.com/liske/needrestart/issues/22#issuecomment-209585427
    case $(sudo needrestart -b 2> /dev/null | grep 'NEEDRESTART-KSTA' | awk '{print $2}') in
        0)
            if grep -qE '(Microsoft|WSL)' /proc/version &> /dev/null; then
                : # running on WSL, no needrestart support yet, skip for now
            else
                echo '[needrestart: unknown]'
            fi
            ;;
        1)
            : # kernel is up-to-date
            ;;
        2)
            echo '[needrestart: kernel upgrade]'
            ;;
        3)
            echo '[needrestart: new kernel version]'
            ;;
        *)
            ;;
    esac
elif [[ $(uname -s) == 'Linux' ]] && sudo -n true &> /dev/null; then
    echo '[needrestart: not installed]'
fi
