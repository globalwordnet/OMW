
# Load the admin.sql schema file and create the admin database
#
# usage: make-admin-db.py DBFILE SCHEMAFILE

import sqlite3
import sys

if len(sys.argv) != 3:
    sys.exit('usage: make-admin-db.py DBFILE SCHEMAFILE')

dbfile = sys.argv[1]
schemafile = sys.argv[2]

con = sqlite3.connect(dbfile)
curs = con.cursor()

f = open(schemafile, 'r')
curs.executescript(f.read())

con.commit()
con.close()
