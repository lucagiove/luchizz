
# START of luchizz bash enhancements
# Copyright (C) 2014-2015 Luca Giovenzana <luca@giovenzana.org>
# luchizz-profile.sh (0.1.0dev)

# colorized prompt
if [ $EUID -eq 0 ]; then
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
alias ack='ack-grep'

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


# enable bash git prompt
if [ -f /usr/local/lib/bash-git-prompt/gitprompt.sh ]; then
   # gitprompt configuration

   # Set config variables first
   GIT_PROMPT_ONLY_IN_REPO=1

   # GIT_PROMPT_FETCH_REMOTE_STATUS=0   # uncomment to avoid fetching remote status

   # GIT_PROMPT_SHOW_UPSTREAM=1 # uncomment to show upstream tracking branch
   # GIT_PROMPT_SHOW_UNTRACKED_FILES=all # can be no, normal or all; determines counting of untracked files

   # GIT_PROMPT_STATUS_COMMAND=gitstatus_pre-1.7.10.sh # uncomment to support Git older than 1.7.10

   # GIT_PROMPT_START=...    # uncomment for custom prompt start sequence
   # GIT_PROMPT_END=...      # uncomment for custom prompt end sequence

   # as last entry source the gitprompt script
   # GIT_PROMPT_THEME=Custom # use custom .git-prompt-colors.sh
   # GIT_PROMPT_THEME=Single_line_Luchizz
   GIT_PROMPT_THEME=Luchizz

    . /usr/local/lib/bash-git-prompt/gitprompt.sh
fi
# END of luchizz bash enhancements
