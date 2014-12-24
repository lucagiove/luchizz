#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright 2014 Luca Giovenzana <luca@giovenzana.org>
#

import sys
from fabric.api import run, sudo


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
    if run('id -u') != '0':
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
