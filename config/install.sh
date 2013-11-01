#!/bin/bash

mkdir -pv /opt/hub
if [[ -w /opt/hub ]]; then
    HUB=/opt/hub
else
    mkdir -pv ${HOME}/hub
    if [[ -w ${HOME}/hub ]]; then
        HUB=${HOME}/hub
    else
        exit 1
    fi
fi
echo "hub is at ${HUB}"

mkdir -pv ${HUB}/fenhl &&
cd ${HUB}/fenhl || exit 1

if which hub; then
    if [[ -d syncbin ]] && hub branch; then
        cd syncbin
        hub pull
    else
        [[ -d syncbin ]] && rm -r syncbin
        hub clone fenhl/syncbin
    fi
elif which git; then
    if [[ -d syncbin ]] && git branch; then
        cd syncbin
        git pull origin master
    else
        [[ -d syncbin ]] && rm -r syncbin
        git clone https://github.com/fenhl/syncbin.git
    fi
else
    echo "missing git command" >&2
    exit 1
fi

mkdir -pv ${HOME}/bin &&
cd ${HOME}/bin &&
CURLSUCCESS=1
if which curl; then
    curl -L http://www.chiark.greenend.org.uk/~sgtatham/utils/lns.tar.gz | tar -xzf -
    CURLSUCCESS=$?
    rm lns.tar.gz
    mv lns .lnsdir
    mv .lnsdir/lns lns
    rm -r .lnsdir
fi
if [[ "$CURLSUCCESS" != "0" ]]; then
    if which wget; then
        wget -O - http://www.chiark.greenend.org.uk/~sgtatham/utils/lns.tar.gz | tar -xzf -
        rm lns.tar.gz
        mv lns .lnsdir
        mv .lnsdir/lns lns
        rm -r .lnsdir
    else
        echo "failed to install lns" >&2
    fi
fi

mkdir -pv ${HUB}/robbyrussell &&
cd ${HUB}/robbyrussell &&
if which hub; then
    if [[ -d oh-my-zsh ]] && hub branch; then
        cd oh-my-zsh &&
        hub pull
    else
        [[ -d oh-my-zsh ]] && rm -r oh-my-zsh
        hub clone robbyrussell/oh-my-zsh
    fi
else
    if [[ -d oh-my-zsh ]] && git branch; then
        cd oh-my-zsh &&
        git pull origin master
    else
        [[ -d oh-my-zsh ]] && rm -r oh-my-zsh
        git clone git://github.com/robbyrussell/oh-my-zsh.git
    fi
fi

if mkdir -pv ${HUB}/robbyrussell/oh-my-zsh/custom/themes; then
    unlink ${HUB}/robbyrussell/oh-my-zsh/custom/themes/fenhl.zsh-theme
    ln -s ${HUB}/fenhl/syncbin/config/fenhl.zsh-theme ${HUB}/robbyrussell/oh-my-zsh/custom/themes/fenhl.zsh-theme
fi

unlink ${HOME}/.zshrc
ln -s ${HUB}/fenhl/syncbin/config/zshrc ${HOME}/.zshrc
unlink ${HOME}/.bash_profile
ln -s ${HUB}/fenhl/syncbin/config/bash_profile ${HOME}/.bash_profile
unlink ${HOME}/.profile
ln -s ${HUB}/fenhl/syncbin/config/profile ${HOME}/.profile

chsh -s /bin/zsh
