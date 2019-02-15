#!/usr/bin/python3

import sys
import sqlite3
import getpass

# It takes one argument: the name of the db
if (len(sys.argv) < 2):
    sys.stderr.write('You need to give the name of the DB\n')
    sys.exit(1)
else:
    u =  sys.argv[0]
    dbfile = sys.argv[1]

pw = getpass.getpass('Please provide an admin password: ')

################################################################
# CONNECT TO DB
################################################################
con = sqlite3.connect(dbfile)
c = con.cursor()

################################################################
# INSERT EXAMPLE USERS DATA (CODES AND NAMES)
################################################################

c.execute("""INSERT INTO users (userID, full_name, password, 
             email, access_level, access_group, affiliation, u)
             VALUES (?,?,?,?,?,?,?,?)""",
          ['admin','System Administrator', pw,
           'changeme@changeme.com', 99, 'admin', 'sys', u])

c.execute("""INSERT INTO users (userID, full_name, password, 
             email, access_level, access_group, affiliation, u)
             VALUES (?,?,?,?,?,?,?,?)""",
          ['user1','System User 1',
           '46bcc2d7eb5723292133857fa95454b9',
           'changeme@changeme.com', 0, 'common', 'sys', u])

con.commit()
con.close()
sys.stderr.write('Loaded example user data in (%s)\n' % (dbfile))
