#!/usr/bin/python3

import sqlite3, sys, nltk
from nltk.corpus import wordnet as wn
from collections import defaultdict as dd


# It takes one argument: the name of the db
if (len(sys.argv) != 3):
    sys.stderr.write('usage: load-ssrels.py DBFILE SSRELFILE\n')
    sys.exit(1)
else:
    u =  sys.argv[0]
    dbfile = sys.argv[1]
    ssrelfile = sys.argv[2]

################################################################
# CONNECT TO DB
################################################################
con = sqlite3.connect(dbfile)
c = con.cursor()

################################################################
# INSERT SSREL DATA
################################################################

f = open(ssrelfile, 'r')
for line in f:
    c.execute("""INSERT INTO ssrel (rel, def, u)
                 VALUES (?,?,?)""", line.strip().split('\t')+[u])
f.close()

con.commit()
con.close()
sys.stderr.write('Loaded SSREL data in (%s)\n' % (dbfile))
