
# START of luchizz bash enhancements
# Copyright (C) 2014-2015 Luca Giovenzana <luca@giovenzana.org>
# luchizz-profile.sh (0.0.8)

# colorized prompt
if [ "`id -u`" -eq 0 ]; then
    PS1='${debian_chroot:+($debian_chroot)}\[\033[01;31m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]# '
else
    PS1='${debian_chroot:+($debian_chroot)}\[\033[01;37m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
fi

# useful aliases
alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'
alias ll='ls -lh'
alias la='ls -A'
alias lal='ls -alh'
alias l='ls -CF'
alias df='df -h'
alias dt='du -sh'
alias free='free -mt'
alias errcho='>&2 echo'

# enable nice colors with ls and grep
if [ "$TERM" != "dumb" ]; then
    eval "`dircolors -b`"
    alias ls='ls --color=auto'
    alias dir='ls --color=auto --format=vertical'
    alias vdir='ls --color=auto --format=long'
    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
fi

# enable bash completion in interactive shells
if ! shopt -oq posix; then
  if [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
  elif [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
  fi
fi

# enable z - jump around module
if [ -f /usr/local/bin/z.sh ]; then
    . /usr/local/bin/z.sh
fi

# END of luchizz bash enhancements

