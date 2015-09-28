#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (C) 2014-2015 Luca Giovenzana <luca@giovenzana.org>
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

import socket
from glob import glob
from fabric.api import run, sudo, put, env, settings
from fabric.context_managers import show, quiet
from fabric.contrib.files import sed, comment, append
from fabric.contrib.files import uncomment, contains, exists

def set_fqdn(fqdn):

    hostname = fqdn.split('.')[0]
    if contains('/etc/hosts', '127.0.1.1'):
        sed('/etc/hosts', '127\.0\.1\.1.*',
            '127\.0\.1\.1\t{}\t{}'.format(fqdn, hostname),
            use_sudo=True)
    else:
        append('/etc/hosts', '127.0.1.1\t{}\t{}'.format(fqdn, hostname),
               use_sudo=True)
    sudo('echo {} >/etc/hostname'.format(hostname))
    # activate the hostname
    sudo('hostname -F /etc/hostname')


def set_rename_user(olduser, newuser):
    # FIXME more strict regex eg. ^user: and pay attention to home folder
    sed('/etc/group', olduser, newuser, use_sudo=True)
    sed('/etc/gshadow', olduser, newuser, use_sudo=True)
    sudo('mv /home/{} /home/{}'.format(olduser, newuser))
    # Is required to run at the same time this two commands otherwise sudo
    # will fail because the password or user has changed
    sudo("sed -i.bak -r -e 's/{}/{}/g' /etc/passwd ;"
         .format(olduser, newuser) +
         "sed -i.bak -r -e 's/{}/{}/g' /etc/shadow"
         .format(olduser, newuser))


def set_serial_console():
    put('./files/ttyS0.conf', '/etc/init/', use_sudo=True)
    sudo('chown root: /etc/init/ttyS0.conf')
    sudo('chmod 644 /etc/init/ttyS0.conf')


def set_authentication_keys():
    """Loops in current user .ssh looking for certificates and ask which one
    needs to be installed remotely"""

    ssh_path = os.path.join(os.getenv('HOME'), '.ssh/')
    ids_ssh = glob('{}id*.pub'.format(ssh_path))
    for id_ssh in ids_ssh:
        with open(id_ssh, 'r') as f:
            # reading the public key for anything after the key to get name and
            # address that normally follow the key
            id_ssh_file = f.read()
        id_ssh_name = ' '.join(id_ssh_file.split()[2:])
        if query_yes_no("CONFIGURE {}'s ssh key for "
                        "authentication?".format(id_ssh_name), 'yes'):
            run('mkdir -p $HOME/.ssh')
            run('touch $HOME/.ssh/authorized_keys')
            append('$HOME/.ssh/authorized_keys', id_ssh_file.rstrip('\n\r'))


def set_gitconfig():
    """If .gitconfig exists for the current user it will
    transfer it remotely"""
    gitconfig_path = os.path.join(os.getenv('HOME'), '.gitconfig')
    put(gitconfig_path, '$HOME/.gitconfig', use_sudo=True)


def luchizz_gitconfig():
    """Setup aliases and gitconfig useful default configurations"""
    with open(os.path.join(LUCHIZZ_DIR, 'files/git_config_commands')) as f:
        git_commands = f.read().split('\n')
    for command in git_commands:
        run(command)


def set_disable_backports():
    # FIXME avoid multiple # to be added if executed multiple times
    comment('/etc/apt/sources.list', '.+-backports', use_sudo=True)


def set_disable_recommended():
    """This method will prevent apt to automatically install recommended
    packages. This is suggested in case you want to have more control of your
    system and keep installed software at minimum"""

    aptconf = """APT::Install-Suggests "0";
APT::Install-Recommends "0";"""
    sudo("echo '{}' > /etc/apt/apt.conf.d/99luchizz".format(aptconf))


def luchizz_shell():
    # Load the luchizz bashrc script
    global LUCHIZZ_DIR
    luchizz_profile = os.path.join(LUCHIZZ_DIR,
                                   'files/profile/luchizz-profile.sh')
    with open(luchizz_profile, 'r') as f:
        luchizz_profile = f.read()

    # Installing default bash changes for newly created users
    # FIXME for what the hell is used this folder?
    # currently this is causing issues if you connect to localhost debug needed
    # new users seems to rely only on /etc/skel/.bashrc
    # ~files = put('./files/profile/*', '/etc/profile.d/', use_sudo=True)
    # ~for f in files:
    # ~sudo('chown root: {}'.format(f))
    # ~sudo('chmod 644 {}'.format(f))

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
        if not exists(bashrc_file, use_sudo=True):
            continue
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
    global LUCHIZZ_DIR
    scripts_dir = os.path.join(LUCHIZZ_DIR, 'files/scripts/*')
    scripts = put(scripts_dir, '/usr/local/bin', use_sudo=True)
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
        sudo('apt-get install shorewall -y')
        sudo('cp /usr/share/doc/shorewall/examples/one-interface/* '
             '/etc/shorewall/')
        rules = """SSH(ACCEPT)         net             $FW"""
        append('/etc/shorewall/rules', rules, use_sudo=True)
        sed('/etc/default/shorewall', 'startup=0', 'startup=1', use_sudo=True)
        sudo('/sbin/shorewall check')
        try:
            # BETTER TO ASK BEFORE TO PREVENT BEING CUT OFF
            # ~sudo('/sbin/shorewall restart')
            pass
        except socket.error:
            pass
    else:
        print("skip, shorewall is already installed!")


def setup_etckeeper():
    if not is_installed('etckeeper'):
        sudo('apt-get install git etckeeper -y')
        comment('/etc/etckeeper/etckeeper.conf', 'VCS="bzr"', use_sudo=True)
        uncomment('/etc/etckeeper/etckeeper.conf', 'VCS="git"', use_sudo=True)
        sudo('etckeeper init')
        sudo('etckeeper commit -m "Initial commit."')
    else:
        print("skip, etckeeper is already installed!")


# ~def setup_mail_notification():
    # ~if not is_installed('ssmtp'):
        # ~sudo('apt-get install ssmtp -y')


def secure_sshd():
    # TODO make sure these line exists
    # PermitEmptyPasswords no
    # PermitRootLogin without-password
    # UseDNS no
    pass


def install_packages(pkgs_list):
    pkgs_string = ""
    for pkg in pkgs_list:
        pkgs_string += " {}".format(pkg)
    with show('stdout', 'stderr'):
        sudo('apt-get install {}'.format(pkgs_string))
