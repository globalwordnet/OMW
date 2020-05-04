#!/usr/bin/python3

import sys
import sqlite3
from getpass import getpass

from omw.common_login import hash_pass

ADMIN_USER = 'admin'
ADMIN_NAME = 'System Administrator'

# It takes one argument: the name of the db
if (len(sys.argv) < 2):
    sys.stderr.write('You need to give the name of the DB\n')
    sys.exit(1)
else:
    u =  sys.argv[0]
    dbfile = sys.argv[1]

print('Creating an admin user.')
print('Username: ' + ADMIN_USER)
print('Full name: ' + ADMIN_NAME)
admin_email = input('Email: ')
admin_pw = hash_pass(getpass('Password: '))

users = [
    (ADMIN_USER, ADMIN_NAME, admin_pw, admin_email, 99, 'admin', 'sys', u)
]

while True:
    print('')
    another = input('Create another user? [y/n]: ')
    if another.lower() in ('n', 'no'):
        break
    elif another.lower() in ('y', 'yes'):
        user = input('Username: ')
        name = input('Full name: ')
        email = input('Email: ')
        pw = hash_pass(getpass('Password: '))
        lvl = 0
        grp = 'common'
        aff = 'sys'
        users.append((user, name, pw, email, lvl, grp, aff, u))
    else:
        print('invalid choice')


################################################################
# CONNECT TO DB
################################################################
con = sqlite3.connect(dbfile)
c = con.cursor()

################################################################
# INSERT EXAMPLE USERS DATA (CODES AND NAMES)
################################################################

for userdata in users:
    c.execute("""
        INSERT INTO users (userID, full_name, password,
        email, access_level, access_group, affiliation, u)
        VALUES (?,?,?,?,?,?,?,?)""",
        userdata)


con.commit()
con.close()
sys.stderr.write('Loaded example user data in (%s)\n' % (dbfile))
