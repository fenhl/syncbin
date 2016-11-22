#!/bin/zsh

for mail_dir in $mailpath; do
    if [[ -d "$mail_dir" ]]; then
        num_mail=$(($(ls -af "$mail_path/cur" | wc -l) - 2))
        if [[ "$num_mail" -gt 0 ]]; then
            echo "[mail: ${num_mail}]"
        fi
    fi
done
