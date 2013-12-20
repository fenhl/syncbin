#!/bin/sh

mkdir -pv /opt/hub
if [ -d /opt/hub ] && [ -w /opt/hub ]; then
    HUB=/opt/hub
else
    mkdir -pv ~/hub
    if [ -d ~/hub ] && [ -w ~/hub ]; then
        HUB=${HOME}/hub
    else
        exit 1
    fi
fi
echo "hub is at" ${HUB}

mkdir -pv ${HUB}/fenhl &&
cd ${HUB}/fenhl || exit 1

if which hub; then
    if [ -d ${HUB}/fenhl/syncbin ] && { cd ${HUB}/fenhl/syncbin; hub branch; }; then
        cd ${HUB}/fenhl/syncbin
        hub pull
    else
        [ -d ${HUB}/fenhl/syncbin ] && rm -r ${HUB}/fenhl/syncbin
        cd ${HUB}/fenhl
        hub clone fenhl/syncbin
    fi
elif which git; then
    if [ -d ${HUB}/fenhl/syncbin ] && { cd ${HUB}/fenhl/syncbin; git branch; }; then
        cd ${HUB}/fenhl/syncbin
        git pull origin master
    else
        [ -d ${HUB}/fenhl/syncbin ] && rm -r ${HUB}/fenhl/syncbin
        cd ${HUB}/fenhl
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
if [ "$CURLSUCCESS" != "0" ]; then
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
    if [ -d ${HUB}/robbyrussell/oh-my-zsh ] && { cd ${HUB}/robbyrussell/oh-my-zsh; hub branch; }; then
        cd ${HUB}/robbyrussell/oh-my-zsh &&
        hub pull
    else
        [ -d ${HUB}/robbyrussell/oh-my-zsh ] && rm -r ${HUB}/robbyrussell/oh-my-zsh
        cd ${HUB}/robbyrussell
        hub clone robbyrussell/oh-my-zsh
    fi
else
    if [ -d ${HUB}/robbyrussell/oh-my-zsh ] && { cd ${HUB}/robbyrussell/oh-my-zsh; git branch; }; then
        cd ${HUB}/robbyrussell/oh-my-zsh &&
        git pull origin master
    else
        [ -d ${HUB}/robbyrussell/oh-my-zsh ] && rm -r ${HUB}/robbyrussell/oh-my-zsh
        cd ${HUB}/robbyrussell
        git clone https://github.com/robbyrussell/oh-my-zsh.git
    fi
fi

if mkdir -pv ${HUB}/robbyrussell/oh-my-zsh/custom/themes; then
    unlink ${HUB}/robbyrussell/oh-my-zsh/custom/themes/fenhl.zsh-theme
    ln -s ${HUB}/fenhl/syncbin/config/fenhl.zsh-theme ${HUB}/robbyrussell/oh-my-zsh/custom/themes/fenhl.zsh-theme
fi

ln -fs ${HUB}/fenhl/syncbin/config/zshrc ~/.zshrc
ln -fs ${HUB}/fenhl/syncbin/config/bash_profile ~/.bash_profile
ln -fs ${HUB}/fenhl/syncbin/config/profile ~/.profile

chsh -s /bin/zsh
