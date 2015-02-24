#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright 2014 Luca Giovenzana <luca@giovenzana.org>
#

import os
import sys
from fabric.api import run, sudo, settings
from fabric.context_managers import quiet


def print_splash(version):
    print """
     _            _     _                           _       _
    | |          | |   (_)                         (_)     | |
    | |_   _  ___| |__  _ ________    ___  ___ _ __ _ _ __ | |_
    | | | | |/ __| '_ \| |_  /_  /   / __|/ __| '__| | '_ \| __|
    | | |_| | (__| | | | |/ / / /    \__ \ (__| |  | | |_) | |_
    |_|\__,_|\___|_| |_|_/___/___|   |___/\___|_|  |_| .__/ \__|
                                                     | |
                                                     |_|
                        version {}
""".format(version)


def check_root():
    """Verifies that the current user is root"""
    with quiet():
        if run('id -u') != '0':
            # FIXME see why doesn't work on raspbmc
            if sudo('id -u', warn_only=True) != '0':
                print """
WARNING: you need to run this script as root or with sudo if you want to take
         advantage of all the luchizz features."""
                sys.exit(1)


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def isdir(path):
    """Test whether a **path** (``str``) is a directory

    Credits to octopus.utils
    """

    with settings(ok_ret_codes=(0, 1)):
        output = run('test -d "%s"' % path, quiet=True)
    if output.return_code == 0:
        return True
    else:
        return False


def listdir(path):
    """Return a list containing the names of the entries in the directory found
    at **path** (str).

    Credits to octopus.utils
    """

    # This is used to add trailing slash if needed and sanitize the input
    path = os.path.join(path, '')
    # Verify that the path exists because the command below wont fail in
    # case the folder doesn't exist.. :(
    if not isdir(path):
        raise OSError('No such file or directory: {}'.format(path))
    # Relies on find to extract non recursive paths
    output = run('find "{}" -maxdepth 1'.format(path), quiet=True)
    # removing extra formatting and the absolute path to simulate the
    # os.listdir() behavior
    dir_list = output.replace('\r', '').replace(path, '').split('\n')
    # Doesn't return the first element which is always "."
    return dir_list[1:]


def listdir_fullpath(path):
    return [os.path.join(path, f) for f in listdir(path)]


def is_installed(package):
    with settings(ok_ret_codes=(0, 1)):
        output = run('dpkg-query -p {}'.format(package), quiet=True)
    if output.return_code == 0:
        return True
    else:
        return False
