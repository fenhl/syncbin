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
    if [[ -z "$VIRTUAL_ENV" ]]; then
        if [[ $(type accio) == "accio is an alias for . accio" ]]; then
            echo '%%'
        else
            echo '%B%F{white}%%%b%f'
        fi
    else
        echo '%B%F{white}P%b%f'
    fi
}

function syncbin-prompt-python-venv {
    if [[ -z "$VIRTUAL_ENV" ]]; then
        return 0 # no venv active
    else
        echo "[venv: $VIRTUAL_ENV]"
    fi
}

function syncbin-prompt-multirust-override {
    if ! where rustup &> /dev/null; then
        if where multirust &> /dev/null; then
            echo "[rust: rustup not installed]"
        else
            return 0 # Rust not installed
        fi
    fi
    if rustup override list | grep 'no overrides' &> /dev/null; then
        return 0 # no overrides
    fi
    multirust_override=$(
        rustup override list |
        grep 'override toolchain' |
        rustup override list |
        awk '{
            res=$2
            split(res, resArr, "-")
            print resArr[1]
        }'
    )
    echo "[rust: ${multirust_override}]"
}

function syncbin-prompt-git-status { # uses modified code from oh-my-git, see the LICENSE
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
        if git branch -a 2> /dev/null | grep '  remotes/origin/HEAD -> origin/' &> /dev/null; then
            head_branch=$(git branch -a 2> /dev/null | grep '  remotes/origin/HEAD -> origin/' | cut -d'/' -f4)
        else
            head_branch='master'
        fi
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

function syncbin-prompt-battery-charge {
    if which batcharge &> /dev/null; then
        echo `batcharge --zsh` 2> /dev/null
    else
        echo '[battery: unknown]'
    fi
}

function syncbin-prompt-disk-space {
    if which diskspace &> /dev/null; then
        echo `diskspace --zsh` 2> /dev/null
    else
        echo '[disk: unknown]'
    fi
}

function syncbin-prompt-needrestart {
    if which needrestart &> /dev/null && sudo -n true &> /dev/null; then
        # https://github.com/liske/needrestart/issues/22#issuecomment-209585427
        case $(sudo needrestart -b | grep 'NEEDRESTART-KSTA' | awk '{print $2}') in
            0)
                echo '[needrestart: unknown]'
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
}

setopt prompt_subst # make sure the functions in the prompts are actually called

PROMPT='[$(syncbin-prompt-user)$(syncbin-prompt-host)$(syncbin-prompt-path)$(syncbin-prompt-shell)] '
RPROMPT='%F{red}$(syncbin-prompt-python-venv)$(syncbin-prompt-multirust-override)$(syncbin-prompt-git-status)$(syncbin-prompt-battery-charge)$(syncbin-prompt-disk-space)$(syncbin-prompt-needrestart)%(?..[exit: %?])%f'
PROMPT2='       zsh %_> '
