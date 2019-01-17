#!/bin/sh

isdeb () {
    if [ "${OSName}" = "Debian" ] || [ "${OSName}" = "Raspbian" ] || [ "${OSName}" = "Ubuntu" ]; then
        return 0
    else
        return 1
    fi
}

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
            git clone https://github.com/"$1"/"$2".git master || return 1
        fi
    else
        echo "\r"'[!!!!]' "missing git command" >&2
        return 1
    fi
}

pi_reinstall=no

# command-line argument parsing
for arg in "$@"; do
    case "$arg" in
        --pi)
            pi_reinstall=yes
            ;;
        *)
            ;;
    esac
done

printf "[....] getting OS"

OSName=$(uname -s)
if [ "${OSName}" = "Linux" ]; then
    if which lsb_release > /dev/null 2>&1; then
        OSName=$(lsb_release -si)
    elif [ -r /etc/redhat-release ]; then
        OSName=$(cat /etc/redhat-release | cut -d' ' -f1)
    elif [ -r /system/build.prop ]; then
        OSName="Android"
    else
        printf ": could not get Linux distro\r[FAIL]"
        echo
        yesno 'continue anyway?' || exit 1
        printf "[....] getting OS"
    fi
elif [ "${OSName}" = "Darwin" ]; then
    OSName="OS X" #TODO change to macOS
else
    echo ": unknown OS: ${OSName}\r[FAIL]"
    exit 1
fi

printf ": ${OSName}\r[ ok ]"
echo

# update APT

if [ "${OSName}" = "Debian" ] || [ "${OSName}" = "Raspbian" ]; then
    if [ $pi_reinstall = no ]; then
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
fi
if isdeb; then
    if ([ $(whoami) = "root" ] || which sudo > /dev/null 2>&1) && ([ $pi_reinstall = yes ] || yesno 'update APT package index now?'); then
        if [ $(whoami) = "root" ]; then
            apt-get update
        elif [ $pi_reinstall = yes ]; then
            sudo apt-get -y update
        else
            sudo apt-get update
        fi
    elif yesno 'APT package index might be outdated, continue anyway?'; then
        : # continue anyway
    else
        exit 1
    fi
fi

# install Zsh

if which zsh > /dev/null 2>&1; then
    : # found zsh
elif isdeb; then
    if yesno 'Zsh not found, install using apt-get?'; then
        if which sudo > /dev/null 2>&1; then
            sudo apt-get install zsh
        else
            apt-get install zsh
        fi
    fi
fi

if which zsh > /dev/null 2>&1; then
    : # found zsh
elif yesno 'Zsh not found, continue anyway?'; then
    : # continue anyway
else
    exit 1
fi

# install and update homebrew

GitInstallInstructions="open GitHub.app and in the Advanced preferences, Install Command Line Tools"

if [ "${OSName}" = "OS X" ]; then
    if which brew > /dev/null 2>&1; then
        : # brew is already installed
    elif which ruby > /dev/null 2>&1 && yesno 'Homebrew not found, install now?'; then
        ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
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

# install git

if which git > /dev/null 2>&1; then
    : # found git
elif isdeb; then
    if yesno 'git not found, install using apt-get?'; then
        if which sudo > /dev/null 2>&1; then
            sudo apt-get install git
        else
            apt-get install git
        fi
    fi
elif [ "${OSName}" = "OS X" ]; then
    if which brew > /dev/null 2>&1 && brew install git; then
        : # git installed
    else
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
        echo '[ ** ] to install git,' ${GitInstallInstructions}
        if [ ${GitInstallInstructions} = "open GitHub.app and in the Advanced preferences, Install Command Line Tools" ] && which open > /dev/null 2>&1; then
            if yesno "open GitHub.app now? (Make sure it's not already open)"; then
                open -nW /Applications/GitHub.app
            fi
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
elif isdeb; then
    if [ $pi_reinstall = yes ] || yesno 'RubyGems not found, install using apt-get?'; then
        if [ $pi_reinstall = yes ]; then
            sudo apt-get -y install ruby
        elif which sudo > /dev/null 2>&1; then
            sudo apt-get install ruby
        else
            apt-get install ruby
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
    if [ $pi_reinstall = yes ] || yesno 'could not create /opt/git/github.com, try using sudo?'; then
        if sudo mkdir -p /opt/git/github.com; then
            if getent group git > /dev/null; then
                sudo chown -R "$(whoami)":git /opt/git
                sudo chmod -R g+rw /opt/git
            else
                sudo chown -R "$(whoami)" /opt/git
            fi
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

if [ "${OSName}" = "Debian" ] || [ "${OSName}" = "Raspbian" ]; then
    if which "command-not-found" > /dev/null 2>&1; then
        : # command-not-found handler already installed
    else
        if [ $pi_reinstall = yes ] || yesno 'command-not-found not found, install using apt-get?'; then
            if [ $pi_reinstall = yes ]; then
                sudo apt-get -y install 'command-not-found'
            elif which sudo > /dev/null 2>&1; then
                sudo apt-get install 'command-not-found'
            else
                apt-get install 'command-not-found'
            fi
            if [ $pi_reinstall = no ] && ([ $(whoami) = "root" ] || which sudo > /dev/null 2>&1) && yesno "edit root's crontab now?"; then
                if [ $(whoami) = "root" ]; then
                    crontab -e
                else
                    sudo crontab -e
                fi
            fi
        fi
    fi
fi

# install Python 3

if [ $pi_reinstall = yes ]; then
    # install Python 3 using Berryconda
    wget -O berryconda-install.sh https://github.com/jjhelmus/berryconda/releases/download/v2.0.0/Berryconda3-2.0.0-Linux-armv7l.sh
    chmod +x berryconda-install.sh
    ./berryconda-install.sh -b
    rm berryconda-install.sh
elif which python3 > /dev/null 2>&1; then
    : # already installed
else
    if [ "${OSName}" = "OS X" ]; then
        brew install python3
    elif yesno 'Python 3 not found, continue anyway?'; then
        : # continue anyway
    else
        exit 1
    fi
fi

# install Python 3 packages

if which python3 > /dev/null 2>&1; then
    if [ $pi_reinstall = yes ] || which pip3 > /dev/null 2>&1; then
        : # found pip3
    elif isdeb; then
        if yesno 'pip3 not found, install using apt-get?'; then
            if which sudo > /dev/null 2>&1; then
                sudo apt-get install python3-pip
            else
                apt-get install python3-pip
            fi
        fi
    fi
    if [ $pi_reinstall = yes ]; then
        ${HOME}/berryconda3/bin/pip install blessings docopt python-mpd2 pytz requests tzlocal # when changing this, also change below
    elif which pip3 > /dev/null 2>&1; then
        : # found Python 3 and pip3, install packages
        if [ $(whoami) = "root" ]; then
            install_python_packages_using_sudo='no'
        elif yesno 'use sudo to install Python packages?'; then
            install_python_packages_using_sudo='yes'
        else
            install_python_packages_using_sudo='no'
        fi
        if [ "${install_python_packages_using_sudo}" = 'yes' ]; then
            sudo pip3 install blessings docopt python-mpd2 pytz requests tzlocal # when changing this, also change above and below
        else
            pip3 install blessings docopt python-mpd2 pytz requests tzlocal # when changing this, also change above
        fi
    elif yesno 'pip3 not found, continue anyway?'; then
        : # continue anyway
    else
        exit 1
    fi
elif yesno 'Python 3 not found, continue anyway?'; then
    : # continue anyway
else
    exit 1
fi

# set up some directories that syncbin tools expect to exist

mkdir -p "${HOME}/.local/share/syncbin"
mkdir -p "${HOME}/.ssh"

# install syncbin

githubinstall fenhl syncbin || exit 1

ln -fs ${HUB}/fenhl/syncbin/master/config/zshenv ~/.zshenv
ln -fs ${HUB}/fenhl/syncbin/master/config/zshrc ~/.zshrc
ln -fs ${HUB}/fenhl/syncbin/master/config/bash_profile ~/.bash_profile
ln -fs ${HUB}/fenhl/syncbin/master/config/profile ~/.profile

if [ $pi_reinstall = yes ]; then
    : # Zsh is already installed and enabled
elif which zsh > /dev/null 2>&1; then
    echo '[ ** ] Looks like syncbin was successfully installed. You can now `chsh -s /bin/zsh` and relog.'
else
    echo '[ ** ] Looks like syncbin was successfully installed. You can now install Zsh, then `chsh -s /bin/zsh` and relog.'
fi

if isdeb && [ $pi_reinstall = no ]; then
    echo '[ ** ] If you have root access, you should also run `syncbin bootstrap debian-root`.`'
fi
