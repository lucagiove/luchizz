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

Usage
-----

For a wizard mode just run the command and follow the instructions:

 ``luchizz``

Or you can specify an host with:

 ``luchizz -H luca@192.160.0.100``

To show available tasks use the fabric command

 ``fab -f tasks.py -l``

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

**Message of the day extra informations**

Now when you connect over ssh to your system you'll be immediately notified with some useful system informations.

For sure you'll never connect to the wrong machine with the new hostname banner.

    Welcome to Ubuntu 14.04.5 LTS (GNU/Linux 4.4.0-34-generic x86_64)
     
               ▄▄▄▄         ██                        
               ▀▀██         ▀▀       ██               
      ▄████▄     ██       ████     ███████    ▄████▄  
     ██▄▄▄▄██    ██         ██       ██      ██▄▄▄▄██
     ██▀▀▀▀▀▀    ██         ██       ██      ██▀▀▀▀▀▀
     ▀██▄▄▄▄█    ██▄▄▄   ▄▄▄██▄▄▄    ██▄▄▄   ▀██▄▄▄▄█
       ▀▀▀▀▀      ▀▀▀▀   ▀▀▀▀▀▀▀▀     ▀▀▀▀     ▀▀▀▀▀  
     
     
      System information as of Thu Aug 25 22:59:55 CEST 2016
 
      System load:     0.88                IP address for wlan0:      192.168.7.102
      Usage of /home:  76.2% of 295.17GB   IP address for lxcbr0:  10.0.3.1
      Memory usage:    52%                 IP address for virbr0:     192.168.122.1
      Swap usage:      5%                  IP address for docker0: 172.17.0.1
      Processes:       307                 IP address for virbr1:  192.168.0.1
       Users logged in: 1
     
      => There are 8 zombie processes.
     
    4 packages can be updated.
    4 updates are security updates.

**Install git configurations and useful aliases**

 If exists a local .gitconfig will push it remotely.

 Useful configurations and aliases
 - safe handlig of crlf
 - push only the current branch
 - fancy colours
 - st = status
 - co = checkout
 - log = log --pretty --decorate
 - hist = log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit
 and more..

**Install git-bash-prompt to always know your git status**

 Integrated https://github.com/magicmonty/bash-git-prompt

 This is what being in a git feature branch will look like:

 ``✔ [devel-0.1 ↓·1|✚ 3…1]``

 ``luca@elite:~/src/luchizz$``


Credits
-------

**Original authors for the bash version:**

Luca Giovenzana - gpg key id: 3B741128  |  Pietro Isotti - gpg key id: A898630F
