**syncbin** is a collection of command-line tools by [Fenhl][], mainly for personal use.

Version
=======

The versioning scheme works as follows:

*   Versions below 1.0 are not versioned and do not auto-update properly; [`install.sh`](config/install.sh) should be run after first installing 1.0 or greater.
*   After the minor version is increased, [`update.sh`](config/update.sh) must be run.
*   After the major version is increased, the patch notes must be displayed and the user is told to re-run `install.sh`.

The current version can be found in [`version.txt`](version.txt).

Installation
============

The following *should* install `syncbin` and a couple of other things like [homebrew][], [oh-my-zsh][], [zsh-completions][]:

```sh
wget -O syncbin-install.sh https://raw.github.com/fenhl/syncbin/master/config/install.sh && sh syncbin-install.sh && rm syncbin-install.sh
```

It is tested on Debian wheezy and OS X Mavericks.

[Fenhl]: http://fenhl.net/ (Fenhl)
[homebrew]: https://github.com/Homebrew/homebrew (github: Homebrew: homebrew)
[oh-my-zsh]: https://github.com/robbyrussell/oh-my-zsh (github: robbyrussell: oh-my-zsh)
[zsh-completions]: https://github.com/zsh-users/zsh-completinos (github: zsh-users: zsh-completions)
