#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2008-2010 by Martin Scharrer <martin@scharrer-online.de>
# All rights reserved.
#
# The i18n support was added by Steffen Hoffmann <hoff.st@web.de>.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# For a copy of the GNU General Public License see
# <http://www.gnu.org/licenses/>.

import getopt
import sys

from trac.env import Environment


def delete_watchlist_tables(envpath, tables=(
        'watchlist', 'watchlist_settings', 'system'), user=None):
    """Deletes all watchlist DB entries => Uninstaller"""
    try:
        env = Environment(envpath)
    except:
        print("Given path '%s' seems not to be a Trac environment." % envpath)
        sys.exit(3)

    with env.db_transaction as db:
        if user is not None:
            if 'watchlist' in tables:
                try:
                    db("DELETE FROM watchlist WHERE wluser=%s", (user,))
                    print("Deleted user entries from 'watchlist' table.")
                except Exception as e:
                    print("Could not delete user entry from 'watchlist' "
                          "table: %s", unicode(e))
            if 'watchlist_settings' in tables:
                try:
                    db("DELETE FROM watchlist_settings WHERE wluser=%s",
                       (user,))
                    print("Deleted user entries from 'watchlist_settings' "
                          "table.")
                except Exception as e:
                    print("Could not delete user entry from "
                          "'watchlist_settings' table: %s" % e)

            print("Finished.")
            return

        if 'watchlist' in tables:
            try:
                db("DROP TABLE watchlist")
                print("Deleted 'watchlist' table.")
            except:
                print("No 'watchlist' table for deletion found.")

        if 'watchlist_settings' in tables:
            try:
                db("DROP TABLE watchlist_settings")
                print("Deleted 'watchlist_settings' table.")
            except:
                print("No 'watchlist_settings' table for deletion found.")

        if 'system' in tables:
            try:
                db("DELETE FROM system WHERE name='watchlist_version'")
                print("Deleted watchlist version entry from system table.")
            except Exception as e:
                print("Could not delete 'watchlist_version' from 'system' "
                      "table: %s", e)

    print("Finished.")


def usage():
    """Trac Watchlist Plugin Uninstaller v1.0 from 24th Sep 2010
     Usage: python uninstall.py [options] /path/to/trac/environment [options]
     Options:
       -h,--help      This help text
       -V,--version   Prints version number and copyright statement
       -u,--user <user>
                      Only remove entries of given user
       -t,--tables <tables>
                      Only removes/uninstalls given tables (default: all).
     Tables:
       watchlist, watchlist_settings, system
    """
    print usage.__doc__


def main(argv):
    tables = ['watchlist', 'watchlist_settings', 'system']
    user = None
    try:
        opts, args = getopt.gnu_getopt(argv, 'hVt:u:',
                                       ['help', 'version', 'tables=',
                                        'user='])
    except getopt.GetoptError as e:
        print unicode(e)
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit()
        elif opt in ('-V', '--version'):
            print __doc__
            sys.exit()
        elif opt in ('-t', '--tables'):
            tables = arg.split(',')
        elif opt in ('-u', '--user'):
            user = arg
    if len(args) < 1:
        print "Error: No trac environment given!"
        usage()
        sys.exit(2)
    else:
        envpath = args[0]

    wtables = [t for t in tables if t != 'system']
    U = ''
    if user is not None:
        U = "all entries of user '%s' from " % user
    print "This will delete " + U + "the following tables: " + ', '.join(
        wtables or ['none'])
    if 'system' in tables and not U:
        print "and remove the 'watchlist_version' from the 'system' table."
    sys.stdout.write("Are you sure? y/N: ")
    if sys.stdin.readline().strip().lower() == 'y':
        delete_watchlist_tables(envpath, tables, user)
    sys.exit()


if __name__ == "__main__":
    main(sys.argv[1:])
