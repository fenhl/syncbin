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
        git_prompt="${git_prompt}?"
    fi
    if [[ $git_status =~ ($'\n'|^).?D ]]; then # removed files
        if [[ ${has_git_status} == "no" ]]; then
            git_prompt="[git: "
        fi
        has_git_status="flags"
        git_prompt="${git_prompt}-"
    fi
    if [[ $git_status =~ ($'\n'|^).?M ]]; then # changed files
        if [[ ${has_git_status} == "no" ]]; then
            git_prompt="[git: "
        fi
        has_git_status="flags"
        git_prompt="${git_prompt}≠"
    fi
    if [[ $git_status =~ ($'\n'|^)A ]]; then # added files
        if [[ ${has_git_status} == "no" ]]; then
            git_prompt="[git: "
        fi
        has_git_status="flags"
        git_prompt="${git_prompt}+"
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
            git_prompt="${git_prompt} "
        fi
        has_git_status="words"
        git_prompt="${git_prompt}${current_branch}"
    fi
    remote_branch="$(git for-each-ref --format='%(upstream:short)' refs/heads/"${current_branch}")"
    if [[ x"$remote_branch" != x"" ]]; then
        current_rev=$(git rev-parse HEAD 2> /dev/null)
        remote_rev=$(git rev-parse origin/"${current_branch}" 2> /dev/null)
        if [[ x$current_rev != x$remote_rev ]]; then
            if [[ ${has_git_status} == "no" ]]; then
                git_prompt="[git: "
            elif [[ ${has_git_status} == "flags" ]]; then
                git_prompt="${git_prompt} "
            elif [[ ${has_git_status} == "words" ]]; then
                git_prompt="${git_prompt} " # space between words
            fi
            has_git_status="words"
            shared_rev=$(git merge-base "$current_rev" "$remote_rev")
            if [[ x$current_rev == x$shared_rev ]]; then
                git_prompt="${git_prompt}(behind)"
            elif [[ x$remote_rev == x$shared_rev ]]; then
                git_prompt="${git_prompt}(ahead)"
            else
                git_prompt="${git_prompt}(diverged)"
            fi
        fi
    fi
    if [[ ${has_git_status} != "no" ]]; then
        has_git_status="end"
        git_prompt="${git_prompt}]"
    fi
    echo ${git_prompt}
fi
