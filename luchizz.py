#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (C) 2014 Luca Giovenzana <luca@giovenzana.org>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

#   ``set`` prefix changes configurations
#   ``setup`` install and configure services
#   ``luchizz`` add nice customizations

import sys
import socket
from optparse import OptionParser
from fabric.api import sudo, put, env, settings
from fabric.contrib.files import sed, comment, append, uncomment
# TODO maybe we can get rid of this dependency to reduce extra libs
from fabtools import system
# Luchizz library
from utils import query_yes_no, check_root, print_splash

__author__ = "Luca Giovenzana <luca@giovenzana.org>"
__date__ = "2014-12-23"
__version__ = "0.0.4dev"

# TODO handle dependencies (fabric, fabtools, pycurl)
# TODO Install packages
# TODO Change default password
# TODO Verify sshd security


def set_hostname(hostname):
    sed('/etc/hosts', '127\.0\.1\.1.*', '127\.0\.1\.1\t'+hostname,
        use_sudo=True)
    system.set_hostname(hostname)

# FIXME run the command
# ~def set_main_user(olduser, newuser):
# ~
    # ~script = """#!/bin/bash
# ~sed -i.bak -r -e 's/%s/%s/g' "$(echo /etc/passwd)"
# ~sed -i.bak -r -e 's/%s/%s/g' "$(echo /etc/shadow)"
# ~sed -i.bak -r -e 's/%s/%s/g' "$(echo /etc/group)"
# ~sed -i.bak -r -e 's/%s/%s/g' "$(echo /etc/gshadow)"
# ~mv /home/%s /home/%s
# ~"""


def set_serial_console():
    put('./files/ttyS0.conf', '/etc/init/', use_sudo=True)
    sudo('chown root: /etc/init/ttyS0.conf')
    sudo('chmod 644 /etc/init/ttyS0.conf')


# ~def set_authkey(user):
    # ~user.add_ssh_public_key(user, '~/.ssh/id_rsa.pub')


def luchizz_shell():
    # Installing default bash changes for new created users
    files = put('./files/profile/*', '/etc/profile.d/', use_sudo=True)
    for f in files:
        sudo('chown root: {}'.format(f))
        sudo('chmod 644 {}'.format(f))

    # Alternate mappings for "page up" and "page down" to search the history
    # uncomment the following lines in /etc/inputrc
    # "\e[5~": history-search-backward
    # "\e[6~": history-search-forward
    uncomment('/etc/inputrc', 'history-search-forward', use_sudo=True)
    uncomment('/etc/inputrc', 'history-search-backward', use_sudo=True)

    # Enable vim syntax
    uncomment('/etc/vim/vimrc', 'syntax on', char='"', use_sudo=True)


def luchizz_scripts():
    scripts = put('./files/scripts/*', '/usr/local/bin', use_sudo=True)
    for s in scripts:
        sudo('chown root: {}'.format(s))
        sudo('chmod 755 {}'.format(s))
    # Restoring no execute permissions for z.sh that doesn't require them
    sudo('chmod 644 /usr/local/bin/z.sh')


def setup_shorewall_one_interface():
    sudo('apt-get install shorewall')
    sudo('cp /usr/share/doc/shorewall/examples/one-interface/* '
         '/etc/shorewall/')
    rules = """SSH(ACCEPT)         net             $FW"""
    append('/etc/shorewall/rules', rules, use_sudo=True)
    sed('/etc/default/shorewall', 'startup=0', 'startup=1', use_sudo=True)
    sudo('/sbin/shorewall check')
    try:
        sudo('/sbin/shorewall restart')
    except socket.error:
        pass


def setup_denyhosts():
    # FIXME not in ubuntu 14.04??
    sudo('apt-get install denyhosts')


def setup_etckeeper():
    sudo('apt-get install git etckeeper -y')
    comment('/etc/etckeeper/etckeeper.conf', 'VCS="bzr"', use_sudo=True)
    uncomment('/etc/etckeeper/etckeeper.conf', 'VCS="git"', use_sudo=True)
    sudo('etckeeper init')
    sudo('etckeeper commit -m "Initial commit."')


def main():
    parser = OptionParser("usage: luchizz.py --host hosts [options]")
    parser.add_option("-H", "--hosts", dest="HOSTS",
                      help="comma-separated list of hosts to operate on",
                      type='string', metavar="HOSTS")
    # parser.add_option("-d", "--debug", dest="DEBUG",
    #                  help="all output from fabric", action='store_true')
    (options, args) = parser.parse_args()
    env.host_string = options.HOSTS.split(',')[0]

    print_splash(__version__)

    proceed = query_yes_no("Do you want to luchizz"
                           "{}?".format(env.host_string), 'no')
    if proceed:
        check_root()

        etckeeper = query_yes_no("""
Would be safer to install etckeeper before changing the etc configurations.
Do you want to proceed?""".format(env.host_string), 'yes')
        if etckeeper:
            setup_etckeeper()

        luchizz_shell()
        luchizz_scripts()
        if etckeeper:
            with settings(ok_ret_codes=(0, 1)):
                sudo('etckeeper commit -m "luchizzed shell"')

        shorewall = query_yes_no("""
Do you want to install shorewall and setup as one interface server?""", 'no')
        if shorewall:
            setup_shorewall_one_interface()

    else:
        print "exiting.."
        sys.exit(0)
    return 0


if __name__ == '__main__':
    main()
