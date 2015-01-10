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

import os
import time
import socket
from optparse import OptionParser
from fabric.api import sudo, put, env, settings
from fabric.contrib.files import sed, comment, append, uncomment, contains
# TODO maybe we can get rid of this dependency to reduce extra libs
from fabtools import system
# Luchizz library
from utils import query_yes_no, check_root, print_splash, listdir_fullpath
from utils import is_installed

__author__ = "Luca Giovenzana <luca@giovenzana.org>"
__date__ = "2015-01-10"
__version__ = "0.0.5dev"

# TODO handle dependencies (fabric, fabtools, pycurl)
# TODO Install packages
# TODO Change default password
# TODO Verify sshd security
# TODO Implement debug mode and remove all the output from fabric


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


def set_authkey():
    # TODO loop in current .ssh user looking for certificates and ask which one
    # needs to be installed remotely, eventually ask to add also to root user
    pass


def luchizz_shell():
    # Load the luchizz bashrc script
    f = open('./files/profile/luchizz-profile.sh', 'r')
    luchizz_profile = f.read()
    f.close()

    # Installing default bash changes for newly created users
    # FIXME for what the hell is used this folder?
    # new users seems to rely only on /etc/skel/.bashrc
    files = put('./files/profile/*', '/etc/profile.d/', use_sudo=True)
    for f in files:
        sudo('chown root: {}'.format(f))
        sudo('chmod 644 {}'.format(f))

    # Update the skel file
    if not contains('/etc/skel/.bashrc', 'luchizz'):
        append('/etc/skel/.bashrc', luchizz_profile, use_sudo=True)
    # Set huge history for newly created users
    sed('/etc/skel/.bashrc', 'HISTSIZE=.*', 'HISTSIZE=1000000', use_sudo=True)
    sed('/etc/skel/.bashrc', 'HISTFILESIZE=.*', 'HISTFILESIZE=100000',
        use_sudo=True)

    # Appending bash changes to current users and root
    homes = listdir_fullpath('/home')
    homes.append('/root')
    for u in homes:
        bashrc_file = os.path.join(u, '.bashrc')
        sed(bashrc_file, 'HISTSIZE=.*', 'HISTIZE=1000000', use_sudo=True)
        sed(bashrc_file, 'HISTFILESIZE=.*', 'HISTFILESIZE=100000',
            use_sudo=True)
        if not contains(bashrc_file, 'luchizz'):
            append(bashrc_file, luchizz_profile, use_sudo=True)

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
    # WARNING UNSTABLE
    # FIXME network cut in case interface is not eth0 but em0 for instance :(
    # TODO maybe is better to install also conntrack
    if not is_installed('shorewall'):
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
    else:
        print("skip, shorewall is already installed!")


def setup_denyhosts():
    # FIXME not in ubuntu 14.04??
    sudo('apt-get install denyhosts')


def setup_etckeeper():
    if not is_installed('etckeeper'):
        sudo('apt-get install git etckeeper')
        comment('/etc/etckeeper/etckeeper.conf', 'VCS="bzr"', use_sudo=True)
        uncomment('/etc/etckeeper/etckeeper.conf', 'VCS="git"', use_sudo=True)
        sudo('etckeeper init')
        sudo('etckeeper commit -m "Initial commit."')
    else:
        print("skip, etckeeper is already installed!")


def secure_sshd():
    # TODO make sure these line exists
    # PermitEmptyPasswords no
    # PermitRootLogin without-password
    pass


def main():
    parser = OptionParser("usage: luchizz.py --host hosts [options]")
    parser.add_option("-H", "--hosts", dest="HOSTS",
                      help="comma-separated list of hosts to operate on",
                      type='string', metavar="HOSTS")
    # parser.add_option("-d", "--debug", dest="DEBUG",
    #                  help="all output from fabric", action='store_true')
    (options, args) = parser.parse_args()
    if options.HOSTS:
        env.host_string = options.HOSTS.split(',')[0]

    print_splash(__version__)
    check_root()
    print("Ready to luchizz: {}\nCTRL-C to abort\n\n".format(env.host_string))
    time.sleep(1)

    # Setup etckeeper
    etckeeper = query_yes_no("Do you want to setup etckeeper to track changes"
                             " in /etc using git?",
                             'yes')
    if etckeeper:
        setup_etckeeper()

    # Luchizz the shell
    shell = query_yes_no("Do you want to luchizz root and all users "
                         "that have the home folder in /home?", 'yes')
    if shell:
        luchizz_shell()
        # If luchizz shell is applied a dedicated commit is applied
        # 127 return code is in case etckeeper is not installed won't fail
        with settings(ok_ret_codes=(0, 1, 127)):
            sudo('etckeeper commit -m "luchizzed shell"')

    # Install luchizz scripts
    scripts = query_yes_no("Do you want to install luchizz scripts in "
                           "/usr/local/bin?", 'yes')
    if scripts:
        luchizz_scripts()

    # ~shorewall = query_yes_no("Do you want to install shorewall and setup "
    # ~"as one interface server?""", 'no')
    # ~if shorewall:
    # ~setup_shorewall_one_interface()

    # Catch all commit for etckeeper
    # 127 return code is in case etckeeper is not installed won't fail
    with settings(ok_ret_codes=(0, 1, 127)):
        sudo('etckeeper commit -m "final luchizz commit"')

    return 0


if __name__ == '__main__':
    main()
