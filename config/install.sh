#!/bin/bash

if mkdir -pv /opt/hub/fenhl; then
    HUB=/opt/hub
elif mkdir -pv ${HOME}/hub/fenhl; then
    HUB=${HOME}/hub
else
    exit 1
fi
echo "hub is at ${HUB}"

cd ${HUB}/fenhl || exit 1

if which hub; then
    rm -r syncbin
    hub clone fenhl/syncbin
elif which git; then
    rm -r syncbin
    git clone https://github.com/fenhl/syncbin.git
else
    exit 1
fi

mkdir -pv ${HOME}/bin &&
cd ${HOME}/bin &&
if which curl; then
    curl -L http://www.chiark.greenend.org.uk/~sgtatham/utils/lns.tar.gz | tar -xzf -
    rm lns.tar.gz
elif which wget; then
    wget -O - http://www.chiark.greenend.org.uk/~sgtatham/utils/lns.tar.gz | tar -xzf -
    rm lns.tar.gz
fi

mkdir -pv ${HUB}/robbyrussell &&
cd ${HUB}/robbyrussell &&
if which hub; then
    rm -r oh-my-zsh
    hub clone robbyrussell/oh-my-zsh
else
    rm -r oh-my-zsh
    git clone git://github.com/robbyrussell/oh-my-zsh.git
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
