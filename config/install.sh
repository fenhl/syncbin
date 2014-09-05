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

githubinstall () {
    printf "[....] installing $2"
    
    if mkdir -p "${HUB}/$1/$2" 2> /dev/null && [ -d "${HUB}/$1/$2" ]; then
        cd "${HUB}/$1/$2"
    else
        echo "\r"'[!!!!]' "could not create directory ${HUB}/$1/$2" >&2
        return 1
    fi
    
    if which git > /dev/null 2>&1; then
        printf " using git\r"'[ ** ]'
        echo
        if [ -d "${HUB}/$1/$2/master" ] && { cd "${HUB}/$1/$2/master"; git branch > /dev/null 2>&1; }; then
            cd "${HUB}/$1/$2/master"
            git pull origin master || return 1
        else
            [ -d "${HUB}/$1/$2/master" ] && rm -r "${HUB}/$1/$2/master"
            cd "${HUB}/$1/$2"
            git clone git@github.com:"$1"/"$2".git master || git clone https://github.com/"$1"/"$2".git master || return 1
        fi
    else
        echo "\r"'[!!!!]' "missing git command" >&2
        return 1
    fi
}

printf "[....] getting OS"

OSName=$(uname -s)
if [ "${OSName}" = "Linux" ]; then
    if which lsb_release > /dev/null 2>&1; then
        OSName=$(lsb_release -si)
    elif [ -r /etc/redhat-release ]; then
        OSName=$(cat /etc/redhat-release | cut -d' ' -f1)
    else
        printf ": could not get Linux distro\r[FAIL]"
        echo
        yesno 'continue anyway?' || exit 1
        printf "[....] getting OS"
    fi
elif [ "${OSName}" = "Darwin" ]; then
    OSName="OS X"
else
    echo ": unknown OS: ${OSName}\r[FAIL]"
    exit 1
fi

printf ": ${OSName}\r[ ok ]"
echo

# modify APT sources.list

if [ "${OSName}" = "Debian" ]; then
    if ([ $(whoami) = "root" ] || which sudo > /dev/null 2>&1) && yesno 'edit APT sources.list now?'; then
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
    if which brew > /dev/null 2>&1; then
        : # brew is already installed
    elif which ruby > /dev/null 2>&1 && yesno 'Homebrew not found, install now?'; then
        ruby -e "$(curl -fsSL https://raw.github.com/Homebrew/homebrew/go/install)"
    fi
    if which brew > /dev/null 2>&1; then
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
    if which brew > /dev/null 2>&1; then
        echo '[ ** ] installing homebrew-cask'
        brew tap phinze/homebrew-cask || GitInstallInstructions="install homebrew-cask and GitHub.app, then ${GitInstallInstructions}"
    else
        echo '[ !! ] Homebrew not found, skipping homebrew-cask install'
    fi
fi

# install GitHub.app

if [ "${OSName}" = "OS X" ]; then
    if which brew > /dev/null 2>&1; then
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

if which git > /dev/null 2>&1; then
    : # found git
elif [ "${OSName}" = "Debian" ]; then
    if yesno 'git not found, install using apt-get?'; then
        if which sudo > /dev/null 2>&1; then
            sudo apt-get install git
        else
            apt-get install git
        fi
    fi
elif [ "${OSName}" = "OS X" ]; then
    echo '[ ** ] to install git,' ${GitInstallInstructions}
    if [ ${GitInstallInstructions} = "open GitHub.app and in the Advanced preferences, Install Command Line Tools" ] && which open > /dev/null 2>&1; then
        if yesno "open GitHub.app now? (Make sure it's not already open)"; then
            open -nW /Applications/GitHub.app
        fi
    fi
fi

if which git > /dev/null 2>&1; then
    : # found git
elif yesno 'git not found, continue anyway?'; then
    : # continue anyway
else
    exit 1
fi

# install RubyGems

if which gem > /dev/null 2>&1; then
    : # found RubyGems
elif [ "${OSName}" = "Debian" ]; then
    if yesno 'RubyGems not found, install using apt-get?'; then
        if which sudo > /dev/null 2>&1; then
            sudo apt-get install rubygems
        else
            apt-get install rubygems
        fi
    fi
fi

if which gem > /dev/null 2>&1; then
    : # found RubyGems
elif yesno 'RubyGems not found, continue anyway?'; then
    : # continue anyway
else
    exit 1
fi

# get hub directory

HUB="unknown"
if mkdir -p /opt/git/github.com 2> /dev/null && [ -d /opt/git/github.com ]; then
    if [ -w /opt/git/github.com ]; then
        HUB=/opt/git/github.com
    else
        if yesno 'no write access to /opt/git/github.com, use anyway?'; then
            HUB=/opt/git/github.com
        else
            HUB=${HOME}/git/github.com
        fi
    fi
elif which sudo > /dev/null 2>&1; then
    if yesno 'could not create /opt/git/github.com, try using sudo?'; then
        if sudo mkdir -p /opt/git/github.com; then
            HUB=/opt/git/github.com
        fi
    fi
fi
if [ ${HUB} = "unknown" ]; then
    if yesno 'could not create /opt/git/github.com, use anyway?'; then
        HUB=/opt/git/github.com
    else
        HUB=${HOME}/git/github.com
    fi
fi
echo "[ ** ] gitdir for GitHub is at" ${HUB}

# install zsh-completions

if [ "${OSName}" = "OS X" ]; then
    brew install zsh-completions
else
    githubinstall zsh-users zsh-completions
fi

# install command-not-found

if [ "${OSName}" = "Debian" ]; then
    if which "command-not-found" > /dev/null 2>&1; then
        : # command-not-found handler already installed
    else
        if yesno 'command-not-found not found, install using apt-get?'; then
            if which sudo > /dev/null 2>&1; then
                sudo apt-get install 'command-not-found'
            else
                apt-get install 'command-not-found'
            fi
            if ([ $(whoami) = "root" ] || which sudo > /dev/null 2>&1) && yesno "edit root's crontab now?"; then
                if [ $(whoami) = "root" ]; then
                    crontab -e
                else
                    sudo crontab -e
                fi
            fi
        fi
    fi
fi

# install lns

if which lns > /dev/null 2>&1; then
    : # lns already installed
elif yesno 'lns not found, download and install now?'; then
    mkdir -p ~/bin &&
    cd ~/bin
    if (which curl > /dev/null 2>&1 && curl -Ls http://www.chiark.greenend.org.uk/~sgtatham/utils/lns.tar.gz | tar -xzf -) || (which wget > /dev/null 2>&1 && wget -qO - http://www.chiark.greenend.org.uk/~sgtatham/utils/lns.tar.gz | tar -xzf -); then
        rm lns.tar.gz
        mv lns .lnsdir
        mv .lnsdir/lns lns
        rm -r .lnsdir
        chmod +x lns
    else
        echo '[ !! ] failed to install lns' >&2
    fi
fi

# install syncbin

githubinstall fenhl syncbin || exit 1

ln -fs ${HUB}/fenhl/syncbin/config/zshenv ~/.zshenv
ln -fs ${HUB}/fenhl/syncbin/config/zshrc ~/.zshrc
ln -fs ${HUB}/fenhl/syncbin/config/bash_profile ~/.bash_profile
ln -fs ${HUB}/fenhl/syncbin/config/profile ~/.profile

echo '[ ** ] Looks like syncbin was successfully installed. You can now `chsh -s /bin/zsh` and relog.'
