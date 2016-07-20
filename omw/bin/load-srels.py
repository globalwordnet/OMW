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
# INSERT SSREL DATA
################################################################

f = open('srel.tab', 'r')
for line in f:
    c.execute("""INSERT INTO srel (rel, def, u) 
                 VALUES (?,?,?)""", line.strip().split('\t')+[u])
f.close()

con.commit()
con.close()
sys.stderr.write('Loaded SREL data in (%s)\n' % (dbfile))
