#!/bin/zsh
# Fenhl's (https://fenhl.net/) personal zsh theme. Can be used with or without oh-my-zsh.

function syncbin-prompt-user {
    if [[ $(whoami) == $DEFAULT_USER ]]; then
        if [[ $(whoami) == root ]]; then
            echo 'root' # always show root user even if it's default for some reason
        fi
    else
        echo '%B%n%b'
    fi
}

function syncbin-prompt-host {
    if [[ -n "$STY" ]] || [[ -n "$SSH_CLIENT" ]] || [[ -n "$SSH_TTY" ]]; then
        echo '%B%m%b' #TODO use night hostname?
    fi
}

function syncbin-prompt-path {
    if ! [[ -d "$(pwd -P)" ]]; then
        echo '%B%F{red}%~%b%f'
    elif [[ $PWD == $HOME ]]; then
        : # omit path
    else
        echo '%B%~%b'
    fi
}

function syncbin-prompt-shell {
    if [[ -n "$VIRTUAL_ENV" ]]; then
        echo '%BP%b' # Python venv
    elif [[ -n "$STY" ]]; then
        echo '%BS%b' # screen
    elif [[ $(type accio) == "accio is an alias for . accio" ]]; then
        echo '%%' # syncbin seems to be fully initialized
    else
        echo '%B?%b' # syncbin not fully initialized
    fi
}

function syncbin-prompt {
    syncbin_prompt_user="$(syncbin-prompt-user)"
    syncbin_prompt_host="$(syncbin-prompt-host)"
    syncbin_prompt_path="$(syncbin-prompt-path)"
    if [[ x"${syncbin_prompt_user}" != x'' ]] && ([[ x"${syncbin_prompt_host}" != x'' ]] || [[ x"${syncbin_prompt_path}" != x'' ]]); then
        syncbin_prompt_sep_user_host='@'
    else
        syncbin_prompt_sep_user_host=''
    fi
    if [[ x"${syncbin_prompt_host}" != x'' ]] && [[ x"${syncbin_prompt_path}" != x'' ]]; then
        syncbin_prompt_sep_host_path=':'
    else
        syncbin_prompt_sep_host_path=''
    fi
    echo "${syncbin_prompt_user}${syncbin_prompt_sep_user_host}${syncbin_prompt_host}${syncbin_prompt_sep_host_path}${syncbin_prompt_path}$(syncbin-prompt-shell) "
}

setopt prompt_subst # make sure the functions in the prompts are actually called

PROMPT='$(syncbin-prompt)'
RPROMPT='%F{red}'
for file in ${GITDIR}/github.com/fenhl/syncbin/master/rprompt/*; do
    RPROMPT+='$('
    RPROMPT+="$file"
    RPROMPT+=')'
done
RPROMPT+='%(?..[exit: %?])%f'
PROMPT2='    zsh %_> '
