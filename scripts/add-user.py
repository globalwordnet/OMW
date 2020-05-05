#!/usr/bin/env python3

import sys
import os
import argparse
import sqlite3
from getpass import getpass

from omw.common_login import hash_pass

parser = argparse.ArgumentParser()
parser.add_argument('db', help='path to the user database')
parser.add_argument('--user', help='username')
parser.add_argument('--name', help='real name')
parser.add_argument('--email', help='email address')
parser.add_argument('--level', type=int, default=0,
                    help='access level (default: 0)')
parser.add_argument('--group', choices=('common', 'admin'), default='common',
                    help='access group (common|admin)')
parser.add_argument('--affiliation', default='sys',
                    help="user's affiliation (default: sys)")
args = parser.parse_args()

if not os.path.isfile(args.db):
    sys.exit('no such database file: ' + str(args.db))

user = args.user
if user is None:
    user = input('Username: ')
assert user, 'A username must be specified.'

name = args.name
if name is None:
    name = input('Full name: ')

email = args.email
if email is None:
    email = input('Email: ')

# hash the password immediately
pw = hash_pass(getpass('Password: '))

level = args.level
group = args.group
affiliation = args.affiliation
u = sys.argv[0]


con = sqlite3.connect(args.db)

with con:
    con.execute("""
        INSERT INTO users (userID, full_name, password, email,
                           access_level, access_group, affiliation, u)
        VALUES (?,?,?,?,?,?,?,?)""",
        (user, name, pw, email, level, group, affiliation, u))

con.close()
