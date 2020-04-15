#!/usr/bin/python3

import sqlite3, sys, nltk
from nltk.corpus import wordnet as wn
from collections import defaultdict as dd

# It takes one argument: the name of the db
if (len(sys.argv) < 2):
    sys.stderr.write('You need to give the name of the DB\n')
    sys.exit(1)
else:
    u =  sys.argv[0]
    dbfile = sys.argv[1]

################################################################
# CONNECT TO DB
################################################################
con = sqlite3.connect(dbfile)
c = con.cursor()

################################################################
# INSERT POS DATA (CODES AND NAMES)
################################################################

### This order is the same order as PWN:
# 1    NOUN 
# 2    VERB 
# 3    ADJECTIVE 
# 4    ADVERB 
# 5    ADJECTIVE SATELLITE 
# https://wordnet.princeton.edu/documentation/senseidx5wn

c.execute("""INSERT INTO pos (tag, def, u) 
           VALUES (?,?,?)""", ['n','noun',u])

c.execute("""INSERT INTO pos (tag, def, u) 
           VALUES (?,?,?)""", ['v','verb',u])

c.execute("""INSERT INTO pos (tag, def, u) 
           VALUES (?,?,?)""", ['a','adjective',u])

c.execute("""INSERT INTO pos (tag, def, u) 
           VALUES (?,?,?)""", ['r','adverb',u])

c.execute("""INSERT INTO pos (tag, def, u) 
           VALUES (?,?,?)""", ['s','adjective satellite',u])

c.execute("""INSERT INTO pos (tag, def, u) 
           VALUES (?,?,?)""", ['c','conjunction',u])

c.execute("""INSERT INTO pos (tag, def, u)
           VALUES (?,?,?)""", ['p','adposition',u])

c.execute("""INSERT INTO pos (tag, def, u) 
           VALUES (?,?,?)""", ['x','non-referential',u])

c.execute("""INSERT INTO pos (tag, def, u) 
           VALUES (?,?,?)""", ['z','phrasets', u])

c.execute("""INSERT INTO pos (tag, def, u) 
           VALUES (?,?,?)""", ['u','unknown',u])

con.commit()
con.close()
sys.stderr.write('Loaded POS data in ({})\n'.format(dbfile))
