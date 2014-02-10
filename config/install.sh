#!/bin/sh

yesno () {
    echo -n "[ ?? ] $1 [y/n] "
    while true; do
        read YesNo
        if [ ${YesNo:=mu} = "Y" ] || [ ${YesNo} = "y" ] || [ ${YesNo} = "yes" ]; then
            return 0
        elif [ ${YesNo} = "N" ] || [ ${YesNo} = "n" ] || [ ${YesNo} = "no" ]; then
            return 1
        fi
        echo -n "[ ?? ] unrecognized answer, type “yes” or “no”: "
    done
}

echo -n "[....] getting OS"

OSName=$(uname -s)
if [ ${OSName} = "Linux" ]; then
    if which lsb_release > /dev/null; then
        OSName=$(lsb_release -si)
    else
        echo ": could not get Linux distro\r[FAIL]"
        exit 1
    fi
elif [ ${OSName} = "Darwin" ]; then
    OSName="OS X"
else
    echo ": unknown OS: ${OSName}\r[FAIL]"
    exit 1
fi

echo ": ${OSName}\r[ ok ]"

# install and update homebrew

GitInstallInstructions="open GitHub.app and in the Advanced preferences, Install Command Line Tools"

if [ ${OSName} = "OS X" ]; then
    if which brew > /dev/null; then
        : # brew is already installed
    elif which ruby > /dev/null && yesno 'Homebrew not found, install now?'; then
        ruby -e "$(curl -fsSL https://raw.github.com/Homebrew/homebrew/go/install)"
    fi
    if which brew > /dev/null; then
        echo '[ ** ] updating Homebrew formulae...'
        brew update
        brew upgrade
    else
        if yesno 'Homebrew not found, continue anyway?'; then
            GitInstallInstructions="install Homebrew, homebrew-cask, and GitHub.app, then ${GitInstallInstructions}"
        else
            exit 1
        fi
    fi
fi

# install homebrew-cask

if [ ${OSName} = "OS X" ]; then
    if which brew > /dev/null; then
        echo '[ ** ] installing homebrew-cask'
        brew tap phinze/homebrew-cask || GitInstallInstructions="install homebrew-cask and GitHub.app, then ${GitInstallInstructions}"
    else
        echo '[ !! ] Homebrew not found, skipping homebrew-cask install'
    fi
fi

# install GitHub.app

if [ ${OSName} = "OS X" ]; then
    if which brew > /dev/null; then
        if brew cask 2>&1 | grep "Unknown command" > /dev/null; then
            echo '[ !! ] homebrew-cask not found, skipping GitHub.app install'
        else
            if brew cask info github | grep "Not installed" > /dev/null; then
                echo '[ ** ] installing GitHub.app'
                brew cask install github || GitInstallInstructions="install GitHub.app, then ${GitInstallInstructions}"
            else
                : # GitHub.app is already installed
            fi
        fi
    else
        echo '[ !! ] Homebrew not found, skipping GitHub.app install'
    fi
fi

# install git

if which git > /dev/null; then
    : # found git
elif [ ${OSName} = "Debian" ]; then
    if yesno 'git not found, install using apt-get?'; then
        if which sudo > /dev/null; then
            sudo apt-get install git
        else
            apt-get install git
        fi
    fi
elif [ ${OSName} = "OS X" ]; then
    echo '[ ** ] to install git,' ${GitInstallInstructions}
    if [ ${GitInstallInstructions} = "open GitHub.app and in the Advanced preferences, Install Command Line Tools" ] && which open > /dev/null; then
        if yesno "open GitHub.app now? (Make sure it's not already open)"
            open -nW /Applications/GitHub.app
        fi
    fi
fi

if which git > /dev/null; then
    : # found git
else
    if yesno 'git not found, continue anyway?'
        : # continue anyway
    else
        exit 1
    fi
fi

# get hub directory

HUB="unknown"
if mkdir -p /opt/hub 2> /dev/null && [ -d /opt/hub ]; then
    if [ -w /opt/hub ]; then
        HUB=/opt/hub
    else
        if yesno 'no write access to /opt/hub, use anyway?'
            HUB=/opt/hub
        else
            HUB=${HOME}/hub
        fi
    fi
elif which sudo > /dev/null; then
    if yesno 'could not create /opt/hub, try using sudo?'
        if sudo mkdir -p /opt/hub; then
            HUB=/opt/hub
        fi
    fi
fi
if [ ${HUB} = "unknown" ]; then
    if yesno 'could not create /opt/hub, use anyway?'
        HUB=/opt/hub
    else
        HUB=${HOME}/hub
    fi
fi
echo "[ ** ] hub is at" ${HUB}

# install syncbin

if mkdir -p ${HUB}/fenhl 2> /dev/null && [ -d ${HUB}/fenhl ]; then
    cd ${HUB}/fenhl
else
    echo '[!!!!]' "could not create directory ${HUB}/fenhl" >&2
    exit 1
fi

if which hub > /dev/null; then
    if [ -d ${HUB}/fenhl/syncbin ] && { cd ${HUB}/fenhl/syncbin; hub branch; }; then
        cd ${HUB}/fenhl/syncbin
        hub pull || exit 1
    else
        [ -d ${HUB}/fenhl/syncbin ] && rm -r ${HUB}/fenhl/syncbin
        cd ${HUB}/fenhl
        hub clone fenhl/syncbin || exit 1
    fi
elif which git > /dev/null; then
    if [ -d ${HUB}/fenhl/syncbin ] && { cd ${HUB}/fenhl/syncbin; git branch; }; then
        cd ${HUB}/fenhl/syncbin
        git pull origin master || exit 1
    else
        [ -d ${HUB}/fenhl/syncbin ] && rm -r ${HUB}/fenhl/syncbin
        cd ${HUB}/fenhl
        git clone git@github.com:fenhl/syncbin.git || exit 1
    fi
else
    echo "missing git command" >&2
    exit 1
fi

mkdir -p ${HUB}/robbyrussell &&
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
        git clone git@github.com:robbyrussell/oh-my-zsh.git
    fi
fi

if mkdir -pv ${HUB}/robbyrussell/oh-my-zsh/custom/themes; then
    ln -fs ${HUB}/fenhl/syncbin/config/fenhl.zsh-theme ${HUB}/robbyrussell/oh-my-zsh/custom/themes/fenhl.zsh-theme
fi

ln -fs ${HUB}/fenhl/syncbin/config/zshenv ~/.zshenv
ln -fs ${HUB}/fenhl/syncbin/config/zshrc ~/.zshrc
ln -fs ${HUB}/fenhl/syncbin/config/bash_profile ~/.bash_profile
ln -fs ${HUB}/fenhl/syncbin/config/profile ~/.profile

echo 'Looks like syncbin was successfully installed. You can now run `chsh -s /bin/zsh`.'
