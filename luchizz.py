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

from tasks import *
# XXX copied pasted import from luchizz to avoid import error clean up needed!!

import os
import sys
import time
import socket
from glob import glob
from optparse import OptionParser
try:
    from fabric.api import run, sudo, put, env, settings
    from fabric.state import output as fabric_output
    from fabric.context_managers import show, quiet
    from fabric.contrib.files import sed, comment, append
    from fabric.contrib.files import uncomment, contains, exists
except ImportError:
    print """
ImportError: Seems that fabric is not installed!
             Try with `sudo pip install fabric`
"""
    sys.exit(1)
try:
    import yaml
except ImportError:
    print """
ImportError: Seems that PyYAML is not installed!
             Try with `sudo pip install pyyaml`
"""
    sys.exit(1)

# Luchizz library
from utils import query_yes_no, check_root, print_splash, listdir_fullpath
from utils import is_installed


__author__ = "Luca Giovenzana <luca@giovenzana.org>"
__date__ = "2016-04-07"
__version__ = "0.1.0dev"

# Luchizz script folder
LUCHIZZ_DIR = os.path.dirname(os.path.realpath(__file__))

# #### future / features
# TODO fix locale error
# TODO setup rkhunter
# TODO setup sshd security
# TODO setup mail notification

# #### version 0.2
# TODO print warning on user rename or change also sudoers
# TODO support line editing for read string
# TODO improve a real debug/verbose/normal mode
# TODO detect luchizz version for the bash-profile and update
# TODO change to argparse

# #### version 0.1
# TODO create setup
# TODO setup travis
# TODO refactor python file structure to split more (maybe tasks.py will solve
# also the below issue)
# TODO clean the list of task shown by fab
# TODO test on 12.04 (16-03-2015 -> OK) and 14.10
# TODO add screenrc profile
# TODO handle CTRL-C interrupt

# #### KNOWN ISSUES
# FIXME handle apt-get update somehow
# FIXME handle returncode 1 in case of NO answer to apt-get
# FIXME handle stdout/err redirection
# FIXME see why doesn't work on raspbmc (bec of motd always printed..)


def main():
    parser = OptionParser("usage: luchizz.py --host hosts [options]",
                          version="luchizz {}".format(__version__))
    parser.add_option("-H", "--hosts", dest="HOSTS",
                      help="comma-separated list of hosts to operate on",
                      type='string', metavar="HOSTS")
    parser.add_option("-p", "--packages-file", dest="PKGS_FILE",
                      help="yaml file for the debian packages you want to "
                      "install via apt-get",
                      type='string', metavar="PKGS_FILE")
    parser.add_option("-d", "--debug", dest="DEBUG",
                      help="all output from fabric", action='store_true',
                      default=False)
    (options, args) = parser.parse_args()

    # Setting up the target hosts
    if options.HOSTS:
        env.host_string = options.HOSTS.split(',')[0]

    # Setting up the default path for the packages yaml
    if not options.PKGS_FILE:
        options.PKGS_FILE = os.path.join(LUCHIZZ_DIR, 'packages.yaml')
    # Make sure the package file exists
    if os.path.isfile(options.PKGS_FILE):
        # get the dictionary from the yaml file
        p = open(options.PKGS_FILE, 'r')
        packages = yaml.load(p.read())
        p.close()
    else:
        print "IOError: packages file not found {}".format(options.PKGS_FILE)
        sys.exit(1)

    # Setting up fabric output for debug
    # FIXME here there are problem with the overrided options context managers
    # needs to be always used probably
    if options.DEBUG:
        to_set = {'aborts': True,
                  'debug': True,
                  'running': True,
                  'status': True,
                  'stderr': True,
                  'stdout': True,
                  'user': True,
                  'warnings': True}
    # Setting up fabric output for normal usage
    else:
        to_set = {'aborts': True,
                  'debug': False,
                  'running': False,
                  'status': False,
                  'stderr': False,
                  'stdout': True,
                  'user': False,
                  'warnings': True}
    # Apply the dictionary structure to the output handler of fabric
    for key in to_set.keys():
        fabric_output[key] = to_set[key]

    print_splash(__version__)
    with quiet():
        check_root()
    print("\nReady to luchizz: {}?\n"
          "CTRL-C to abort\n".format(env.host_string))
    time.sleep(1)

    # Setup etckeeper
    if not is_installed('etckeeper'):
        if query_yes_no("SETUP: etckeeper to track changes in /etc "
                        "using git?", 'yes'):
            setup_etckeeper()

    # Luchizz the shell
    if query_yes_no("CONFIGURE: do you want to `luchizz` root and all users "
                    "with a home folder in /home?", 'yes'):
        with quiet():
            luchizz_shell()
        # If luchizz shell is applied a dedicated commit is applied
        # 127 return code is in case etckeeper is not installed won't fail
        with settings(ok_ret_codes=(0, 1, 127)), quiet():
            sudo('etckeeper commit -m "luchizzed shell"')

    # Install luchizz scripts
    if query_yes_no("INSTALL: luchizz scripts in /usr/local/bin?", 'yes'):
        with quiet():
            luchizz_scripts()

    # Copy ssh keys
    if query_yes_no("CONFIGURE: local ssh keys as authorized for "
                    "authentication?", 'yes'):
        with quiet():
            set_ssh_keys()

    # Copy .gitconfig
    if os.path.isfile(os.path.join(os.getenv('HOME'), '.gitconfig')):
        if query_yes_no("COPY: .gitconfig file from the local user?",
                        'yes'):
            with quiet():
                set_gitconfig()

    if query_yes_no("CONFIGURE: do you want to luchizz the .gitconfig for the "
                    "current user?", 'yes'):
            with quiet():
                luchizz_gitconfig()

    if query_yes_no("INSTALL: bash-git-prompt extension in /usr/local/lib?",
                    'yes'):
            with quiet():
                setup_bash_git_prompt()

    # Disable backports
    if query_yes_no("DISABLE: backports repositories?", 'yes'):
        with quiet():
            set_disable_backports()

    # Disable automatic installation of suggested and recommended packages
    if query_yes_no("DISABLE: automatic installation of recommended packages?",
                    'yes'):
        with quiet():
            set_disable_recommended()

    for pkg_section in packages.keys():
        if query_yes_no("INSTALL: {} packages?".format(pkg_section),
                        'yes'):
            install_packages(packages[pkg_section])

    # ~shorewall = query_yes_no("Do you want to install shorewall and setup "
    # ~"as one interface server?""", 'no')
    # ~if shorewall:
    # ~setup_shorewall_one_interface()

    # Catch all commit for etckeeper
    # 127 return code is in case etckeeper is not installed won't fail
    with settings(ok_ret_codes=(0, 1, 127)), quiet():
        sudo('etckeeper commit -m "final luchizz commit"')

    print "\nluchizz done"
    return 0


if __name__ == '__main__':
    main()
