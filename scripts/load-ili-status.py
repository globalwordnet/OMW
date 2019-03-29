#!/usr/bin/python3

import sqlite3, sys

# It takes one argument: the name of the new database
if (len(sys.argv) < 1):
    sys.stderr.write('You need to give the name of the ILI DB\n')
    sys.exit(1)
else:
    dbfile = sys.argv[1]


################################################################
# CONNECT TO DB
################################################################
con = sqlite3.connect(dbfile)
c = con.cursor()

################################################################
# USER
################################################################

u = "ili_load-status.py"

################################################################
# INSERT POS DATA (CODES AND NAMES)
################################################################

c.execute("""INSERT INTO status (id, status, u) 
           VALUES (?,?,?)""", [0,'deprecated',u])

c.execute("""INSERT INTO status (id, status, u) 
           VALUES (?,?,?)""", [1,'normal',u])

c.execute("""INSERT INTO status (id, status, u) 
           VALUES (?,?,?)""", [2,'temporary',u])

con.commit()
con.close()
sys.stderr.write('Loaded STATUS data in (%s)\n' % (dbfile))
