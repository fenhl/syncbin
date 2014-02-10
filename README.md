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

The following *should* install `syncbin` and [oh-my-zsh][]:

```sh
wget -O syncbin-install.sh https://raw.github.com/fenhl/syncbin/master/config/install.sh && sh syncbin-install.sh && rm syncbin-install.sh
```

From my experience, it's almost guaranteed to not work though.

[Fenhl]: http://fenhl.net/ (Fenhl)
[oh-my-zsh]: https://github.com/robbyrussell/oh-my-zsh (github: robbyrussell: oh-my-zsh)
