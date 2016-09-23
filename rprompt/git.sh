#!/bin/zsh

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
