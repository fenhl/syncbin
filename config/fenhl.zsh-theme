#!/bin/zsh
# Fenhl's (http://fenhl.net/) personal zsh theme. Can be used with or without oh-my-zsh.

function syncbin-prompt-user {
    if [[ $(whoami) == $DEFAULT_USER ]]; then
        if [[ $(whoami) == root ]]; then
            echo '#'
        else
            echo ' '
        fi
    elif [[ $(whoami) == root ]]; then
        echo '%B%F{white}#%b%f'
    else
        echo '%B%F{white}'$(whoami | cut -c 1)'%b%f'
    fi
}

function syncbin-prompt-host {
    if hostname -f &> /dev/null; then
        if [[ $(hostname -f) =~ ^$DEFAULT_HOST ]]; then
            echo ' '
        else
            echo '%B%F{white}'$(hostname -f | cut -c 1)'%b%f'
        fi
    else
        echo '%B%F{white}?%b%f'
    fi
}

function syncbin-prompt-path {
    if [[ $PWD == $HOME ]]; then
        echo ' '
    elif [[ $PWD == '/' ]]; then
        echo '%B%F{white}/%b%f'
    elif (( $+path[(r)$PWD] )); then
        echo '%B%F{white}b%b%f'
    elif git branch &> /dev/null; then
        echo '%B%F{white}g%b%f'
    elif hg root &> /dev/null; then
        echo '%B%F{white}m%b%f'
    elif ishome &> /dev/null; then
        echo '%B%F{white}~%b%f'
    else
        echo '%B%F{white}.%b%f'
    fi
}

function syncbin-prompt-shell {
    if [[ -n "$VIRTUAL_ENV" ]]; then
        echo '%B%F{white}P%b%f'
    elif screen -ls | grep '\(Attached\)' > /dev/null; then
        echo '%B%F{white}S%b%f'
    elif [[ $(type accio) == "accio is an alias for . accio" ]]; then
        echo '%%'
    else
        echo '%B%F{white}%%%b%f'
    fi
}

setopt prompt_subst # make sure the functions in the prompts are actually called

PROMPT='[$(syncbin-prompt-user)$(syncbin-prompt-host)$(syncbin-prompt-path)$(syncbin-prompt-shell)] '
RPROMPT='%F{red}'
for file in ${GITDIR}/github.com/fenhl/syncbin/master/rprompt/*; do
    RPROMPT+='$('
    RPROMPT+="$file"
    RPROMPT+=')'
done
RPROMPT+='%(?..[exit: %?])%f'
PROMPT2='       zsh %_> '
