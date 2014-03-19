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
    elif (( $+path[(r)$PWD] )); then
        if [[ $PWD == $HOME ]]; then
            echo 'b'
        else
            echo '%B%F{white}b%b%f'
        fi
    elif git branch &> /dev/null; then
        if [[ $PWD == $HOME ]]; then
            echo 'g'
        else
            echo '%B%F{white}g%b%f'
        fi
    elif hg root &> /dev/null; then
        if [[ $PWD == $HOME ]]; then
            echo 'm'
        else
            echo '%B%F{white}m%b%f'
        fi
    elif ishome &> /dev/null; then 
        if [[ $PWD == $HOME ]]; then
            echo '~'
        else
            echo '%B%F{white}~%b%f'
        fi
    else
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
        if [[ $git_status =~ ($'\n'|^)'\?\?' ]]; then # untracked files
            if [[ ${has_git_status} == "no" ]]; then
                git_prompt="[git: "
            fi
            has_git_status="flags"
            git_prompt=${git_prompt}"?"
        fi
        if [[ $git_status =~ ($'\n'|^).?D ]]; then # removed files
            if [[ ${has_git_status} == "no" ]]; then
                git_prompt="[git: "
            fi
            has_git_status="flags"
            git_prompt=${git_prompt}"-"
        fi
        if [[ $git_status =~ ($'\n'|^).?M ]]; then # changed files
            if [[ ${has_git_status} == "no" ]]; then
                git_prompt="[git: "
            fi
            has_git_status="flags"
            git_prompt=${git_prompt}"≠"
        fi
        if [[ $git_status =~ ($'\n'|^)A ]]; then # added files
            if [[ ${has_git_status} == "no" ]]; then
                git_prompt="[git: "
            fi
            has_git_status="flags"
            git_prompt=${git_prompt}"+"
        fi
        head_branch=$(git for-each-ref --format=$'%(objectname)\t%(refname)' 2> /dev/null | grep $'\trefs/remotes/origin/HEAD' | cut -f1)
        head_branch=$(git for-each-ref --format=$'%(objectname)\t%(refname)' 2> /dev/null | grep '^'${head_branch}$'\t'refs/remotes/origin/ | grep -v /HEAD'$' | cut -f2 | cut -d'/' -f4)
        if [[ "${head_branch}" != "${current_branch}" ]]; then
            if [[ ${has_git_status} == "no" ]]; then
                git_prompt="[git: "
            elif [[ ${has_git_status} == "flags" ]]; then
                git_prompt=${git_prompt}" "
            fi
            has_git_status="branch"
            git_prompt="${git_prompt}${current_branch}"
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
        echo `batcharge --zsh` 2> /dev/null
    else
        echo '[battery: unknown]'
    fi
}

function disk_space {
    if which diskspace &> /dev/null; then
        echo `diskspace --zsh` 2> /dev/null
    else
        echo '[disk: unknown]'
    fi
}

PROMPT='[$(user)$(host)$(path)$(prompt_symbol)] '
RPROMPT='%F{red}$(git_status)$(battery_charge)$(disk_space)%(?..[exit: %?])%f'
PROMPT2='zsh %_> '
