luchizz
=======

**Make any Linux shell like home.**

Tested on:
 - Ubuntu 14.04 Trusty
 - Debian 7.7 Wheezy

Luchizz was originally implemented as bash script to modify a Linux
installation to be more comfortable and usable with some customization
especially for shell usage.
With this github repo I'm starting to rewrite the script in python using fabric
library in order to deploy remotely (via ssh) commonly used packages and shell
improvements.

Features
--------

**Shell improvements**

 - Pag UP/DOWN to search in the command history
 - Different prompt colors for normal user and root
 - Human readable output for ls, df, free
 - Colorized output for ls, grep
 - Overwrite protection with --interactive aliases for rm, cp, mv
 - Extended command history
 and more..

**Quick packages deployment**

 Luchizz script has a default ``packages.yaml`` with categorized sections for
 packages to be installed.
 List of common used packages can be easily extended and customized.

**Extra commands**

 - ``z`` jump around shell script
 - ``detectip`` what's my ip command
 - ``repo`` from http://source.android.com/source/downloading.html

**Apt tuning**

 - Disable backports repository (normally less stable and reliable)
 - Disable automatic installation for recommended and suggested packages

**Install ssh keys for authentication**
 
 For each ``.pub`` key in ``$HOME/.ssh`` will be prompted a request to copy the
 public certificate to the remote system ``authorized_key``.
 
 **Install git configurations and useful aliases**
 
 If exists a local .gitconfig will push it remotely

Credits
-------

**Original authors for the bash version:**

Luca Giovenzana - gpg key id: 3B741128  |  Pietro Isotti - gpg key id: A898630F

