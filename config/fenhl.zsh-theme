#-------------------------------------------------------------------------------
# Fenhl's (http://fenhl.net/) personal oh-my-zsh theme
# (Needs git plugin)
#-------------------------------------------------------------------------------

function user {
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

function host {
    if hostname -f &> /dev/null; then
        if [[ $DEFAULT_HOST == $(hostname -f) ]] || $(which localhost &> /dev/null) && [[ $(localhost) == "fenubookair" ]]; then
            echo ' '
        else
            echo '%B%F{white}'$(hostname -f | cut -c 1)'%b%f'
        fi
    else
        echo '%B%F{white}?%b%f'
    fi
}

function path {
    if [[ $PWD == '/' ]]; then
        if [[ $PWD == $HOME ]]; then
            echo '/'
        else
            echo '%B%F{white}/%b%f'
        fi
    elif [[ $PWD == $HOME ]]; then
        echo '~'
    elif (( $+path[(r)$PWD] )); then
        echo '%B%F{white}b%b%f'
    else
        git branch >/dev/null 2>/dev/null && echo '%B%F{white}g%b%f' && return
        hg root >/dev/null 2>/dev/null && echo '%B%F{white}m%b%f' && return
        echo '%B%F{white}.%b%f'
    fi
}

function prompt_symbol {
    if [[ $(type accio) == "accio is an alias for . accio" ]]; then
        echo '%%'
    else
        echo '%B%F{white}%%%b%f'
    fi
}

function battery_charge {
    if which batcharge &> /dev/null; then
        echo `batcharge --zsh` 2>/dev/null
    else
        echo '[battery: unknown]'
    fi
}

ZSH_THEME_GIT_PROMPT_PREFIX="[git: "
ZSH_THEME_GIT_PROMPT_SUFFIX="]"
ZSH_THEME_GIT_PROMPT_DIRTY=" %F{red}(dirty)%f"

PROMPT='[$(user)$(host)$(path)$(prompt_symbol)] '
RPROMPT='$(git_prompt_info)%F{red}$(battery_charge)%(?..[exit: %?])%f'
PROMPT2='zsh %_> '
