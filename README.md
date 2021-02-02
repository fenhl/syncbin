This is [Fenhl](https://fenhl.net/)'s **syncbin**.

A syncbin, also called dotfiles, is a collection of command-line tools and configuration, mainly for personal use. However, this one is easy to install and automatically updates itself, so you're welcome to check it out even if you're not Fenhl.

# Version

The versioning scheme works as follows:

* Versions below 1.0 are not versioned and do not auto-update properly; [`install.sh`](config/install.sh) should be run after first installing 1.0 or greater.
* After the minor version is increased, [`syncbin-update`](syncbin-update) must be run. This is done automatically by the [`zshrc`](config/zshrc).
* After the major version is increased, the instructions in the patch notes must be followed.

The current version can be found in [`version.txt`](version.txt).

# Installation

The following *should* install `syncbin` and a couple of other things like [homebrew](https://brew.sh/), [oh-my-zsh](https://github.com/robbyrussell/oh-my-zsh), [zsh-completions](https://github.com/zsh-users/zsh-completions):

```sh
curl --proto '=https' --tlsv1.2 -sSf https://start.fenhl.net | sh
```

It was last tested on Debian jessie, Raspbian buster, Ubuntu Artful Aardvark, macOS Mojave, and CentOS 6.5. If it doesn't work for you, feel free to open an issue.
