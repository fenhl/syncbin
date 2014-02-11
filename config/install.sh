#!/bin/sh

yesno () {
    printf "[ ?? ] $1 [y/n] "
    while true; do
        read YesNo
        if [ ${YesNo:=mu} = "Y" ] || [ ${YesNo} = "y" ] || [ ${YesNo} = "yes" ]; then
            return 0
        elif [ ${YesNo} = "N" ] || [ ${YesNo} = "n" ] || [ ${YesNo} = "no" ]; then
            return 1
        fi
        printf "[ ?? ] unrecognized answer, type “yes” or “no”: "
    done
}

github-install () {
    printf "[....] installing $2"
    
    if mkdir -p ${HUB}/"$1" 2> /dev/null && [ -d ${HUB}/"$1" ]; then
        cd ${HUB}/"$1"
    else
        echo "\r"'[!!!!]' "could not create directory ${HUB}/$1" >&2
        return 1
    fi
    
    if which hub > /dev/null; then
        echo " using hub\r"'[ ** ]'
        if [ -d ${HUB}/"$1"/"$2" ] && { cd ${HUB}/"$1"/"$2"; hub branch > /dev/null 2>&1; }; then
            cd ${HUB}/"$1"/"$2"
            hub pull || return 1
        else
            [ -d ${HUB}/"$1"/"$2" ] && rm -r ${HUB}/"$1"/"$2"
            cd ${HUB}/"$1"
            hub clone "$1"/"$2" || return 1
        fi
    elif which git > /dev/null; then
        echo " using git\r"'[ ** ]'
        if [ -d ${HUB}/"$1"/"$2" ] && { cd ${HUB}/"$1"/"$2"; git branch > /dev/null 2>&1; }; then
            cd ${HUB}/"$1"/"$2"
            git pull origin master || return 1
        else
            [ -d ${HUB}/"$1"/"$2" ] && rm -r ${HUB}/"$1"/"$2"
            cd ${HUB}/"$1"
            git clone git@github.com:"$1"/"$2".git || return 1
        fi
    else
        echo "\r"'[!!!!]' "missing git command" >&2
        return 1
    fi
}

printf "[....] getting OS"

OSName=$(uname -s)
if [ "${OSName}" = "Linux" ]; then
    if which lsb_release > /dev/null; then
        OSName=$(lsb_release -si)
    else
        echo ": could not get Linux distro\r[FAIL]"
        exit 1
    fi
elif [ "${OSName}" = "Darwin" ]; then
    OSName="OS X"
else
    echo ": unknown OS: ${OSName}\r[FAIL]"
    exit 1
fi

echo ": ${OSName}\r[ ok ]"

# modify APT sources.list

if [ "${OSName}" = "Debian" ]; then
    if ([ $(whoami) = "root" ] || which sudo > /dev/null) && yesno 'edit APT sources.list now?'; then
        if [ $(whoami) = "root" ]; then
            ${EDITOR:=nano} /etc/apt/sources.list
        else
            sudo ${EDITOR:=nano} /etc/apt/sources.list
        fi
    elif yesno 'APT sources.list might be outdated or misconfigured, continue anyway?'; then
        : # continue anyway
    else
        exit 1
    fi
fi

# install and update homebrew

GitInstallInstructions="open GitHub.app and in the Advanced preferences, Install Command Line Tools"

if [ "${OSName}" = "OS X" ]; then
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

if [ "${OSName}" = "OS X" ]; then
    if which brew > /dev/null; then
        echo '[ ** ] installing homebrew-cask'
        brew tap phinze/homebrew-cask || GitInstallInstructions="install homebrew-cask and GitHub.app, then ${GitInstallInstructions}"
    else
        echo '[ !! ] Homebrew not found, skipping homebrew-cask install'
    fi
fi

# install GitHub.app

if [ "${OSName}" = "OS X" ]; then
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
elif [ "${OSName}" = "Debian" ]; then
    if yesno 'git not found, install using apt-get?'; then
        if which sudo > /dev/null; then
            sudo apt-get install git
        else
            apt-get install git
        fi
    fi
elif [ "${OSName}" = "OS X" ]; then
    echo '[ ** ] to install git,' ${GitInstallInstructions}
    if [ ${GitInstallInstructions} = "open GitHub.app and in the Advanced preferences, Install Command Line Tools" ] && which open > /dev/null; then
        if yesno "open GitHub.app now? (Make sure it's not already open)"; then
            open -nW /Applications/GitHub.app
        fi
    fi
fi

if which git > /dev/null; then
    : # found git
elif yesno 'git not found, continue anyway?'; then
    : # continue anyway
else
    exit 1
fi

# install RubyGems

if which gem > /dev/null; then
    : # found RubyGems
elif [ "${OSName}" = "Debian" ]; then
    if yesno 'RubyGems not found, install using apt-get?'; then
        if which sudo > /dev/null; then
            sudo apt-get install rubygems
        else
            apt-get install rubygems
        fi
    fi
fi

if which gem > /dev/null; then
    : # found RubyGems
elif yesno 'RubyGems not found, continue anyway?'; then
    : # continue anyway
else
    exit 1
fi

# install hub

if which hub > /dev/null; then
    : # found hub
elif [ "${OSName}" = "OS X" ] && which brew > /dev/null; then
    echo '[ ** ] installing hub'
    brew install hub
else
    if which gem > /dev/null && yesno 'hub not found, install using RubyGems?'; then
        if gem install hub; then
            : # successfully installed
        elif which sudo > /dev/null && yesno 'could not install hub, try with sudo?'; then
            sudo gem install hub
        fi
    fi
fi

if which hub > /dev/null; then
    : # found hub
elif yesno 'hub not found, continue anyway?'; then
    : # continue anyway
else
    exit 1
fi

# get hub directory

HUB="unknown"
if mkdir -p /opt/hub 2> /dev/null && [ -d /opt/hub ]; then
    if [ -w /opt/hub ]; then
        HUB=/opt/hub
    else
        if yesno 'no write access to /opt/hub, use anyway?'; then
            HUB=/opt/hub
        else
            HUB=${HOME}/hub
        fi
    fi
elif which sudo > /dev/null; then
    if yesno 'could not create /opt/hub, try using sudo?'; then
        if sudo mkdir -p /opt/hub; then
            HUB=/opt/hub
        fi
    fi
fi
if [ ${HUB} = "unknown" ]; then
    if yesno 'could not create /opt/hub, use anyway?'; then
        HUB=/opt/hub
    else
        HUB=${HOME}/hub
    fi
fi
echo "[ ** ] hub is at" ${HUB}

# install zsh-completions

if [ "${OSName}" = "OS X" ]; then
    brew install zsh-completions
else
    github-install zsh-users zsh-completions
fi

# install syncbin

github-install fenhl syncbin || exit 1

# install oh-my-zsh

github-install robbyrussell oh-my-zsh || exit 1

if mkdir -p ${HUB}/robbyrussell/oh-my-zsh/custom/themes && [ -w ${HUB}/robbyrussell/oh-my-zsh/custom/themes ]; then
    ln -fs ${HUB}/fenhl/syncbin/config/fenhl.zsh-theme ${HUB}/robbyrussell/oh-my-zsh/custom/themes/fenhl.zsh-theme
else
    echo '[ !! ]' "could not install oh-my-zsh theme"
fi

ln -fs ${HUB}/fenhl/syncbin/config/zshenv ~/.zshenv
ln -fs ${HUB}/fenhl/syncbin/config/zshrc ~/.zshrc
ln -fs ${HUB}/fenhl/syncbin/config/bash_profile ~/.bash_profile
ln -fs ${HUB}/fenhl/syncbin/config/profile ~/.profile

echo '[ ** ] Looks like syncbin was successfully installed. You can now `chsh -s /bin/zsh` and relog.'
