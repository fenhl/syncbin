#-------------------------------------------------------------------------------
# Fenhl's (http://fenhl.net/) personal oh-my-zsh theme
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

function git_status { # uses modified code from oh-my-git, see the LICENSE
    has_git_status="no"
    git_prompt=""
    current_commit_hash=$(git rev-parse HEAD 2> /dev/null)
    if [[ -n $current_commit_hash ]]; then
        current_branch=$(git rev-parse --abbrev-ref HEAD 2> /dev/null)
        git_status=$(git status --porcelain 2> /dev/null)
        if [[ $git_status =~ ($'\n'|^).D ]] || [[ $git_status =~ ($'\n'|^)D ]]; then
            if [[ ${has_git_status} == "no" ]]; then
                git_prompt="[git: "
            fi
            has_git_status="flags"
            git_prompt=${git_prompt}"-"
        fi
        if [[ $git_status =~ ($'\n'|^).M ]] || [[ $git_status =~ ($'\n'|^)M ]]; then
            if [[ ${has_git_status} == "no" ]]; then
                git_prompt="[git: "
            fi
            has_git_status="flags"
            git_prompt=${git_prompt}"≠"
        fi
        if [[ $git_status =~ ($'\n'|^)A ]]; then
            if [[ ${has_git_status} == "no" ]]; then
                git_prompt="[git: "
            fi
            has_git_status="flags"
            git_prompt=${git_prompt}"+"
        fi
        if [[ ${has_git_status} != "no" ]]; then
            has_git_status="end"
            git_prompt=${git_prompt}"]"
        fi
        echo ${git_prompt}
    fi
}

function battery_charge {
    if which batcharge &> /dev/null; then
        echo `batcharge --zsh` 2>/dev/null
    else
        echo '[battery: unknown]'
    fi
}

PROMPT='[$(user)$(host)$(path)$(prompt_symbol)] '
RPROMPT='%F{red}$(git_status)$(battery_charge)%(?..[exit: %?])%f'
PROMPT2='zsh %_> '
