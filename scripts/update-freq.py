##
## update the frequencies in the sense meta tables
##

import sys, sqlite3
from warnings import warn

from collections import defaultdict as dd

# It takes one argument: the name of the db
if (len(sys.argv) < 2):
    sys.stderr.write('You need to give the name of the DB\n')
    sys.exit(1)
else:
    u =  sys.argv[0]
    dbfile = sys.argv[1]


# dbfile = "../db/omw.db"
con = sqlite3.connect(dbfile)
c = con.cursor()

sfreq=dd(int)


c.execute("""SELECT s_id, x3 FROM sxl WHERE x1='freq'""")
for (s_id, count) in c:
    sfreq[s_id] += int(count)

smt_id = None
uname= 'update-freq.py'   
c.execute("""SELECT id FROM smt WHERE tag='freq'""")
r = c.fetchone()
if r:
    smt_id = r[0]
else:
    c.execute("""INSERT INTO smt(tag, name, u) VALUES (?,?,?)""",
              ('freq', 'frequency', uname))
    smt_id=c.lastrowid

update={}
delete=set()
c.execute("""SELECT s_id,  sml_id  FROM sm WHERE smt_id =?""", (smt_id,))
for (s_id,  sml_id)  in c:
    if s_id in sfreq:
        if sml_id != sfreq[s_id]:  ### new value for frequency
            update[s_id] = sml_id
        del sfreq[s_id]  ### either it is unchanged or we update it
    else:
        warn("No frequency for {} (was {})".format(s_id, sml_id))
        delete.add(s_id)
###
### anything left in sfreq must be added
###
#print (smt_id)
c.executemany("""
INSERT OR REPLACE 
INTO sm (s_id, smt_id, sml_id, u)
VALUES (?, ?, ?, ?)""",
              [(s_id, smt_id, count, uname)
               for (s_id, count) in sfreq.items() if count > 0])
###
### update changed values
###
c.executemany("""
UPDATE sm SET sml_id=? 
WHERE s_id = ? AND smt_id=?""",
              [(count, s_id, smt_id)
               for (s_id, count) in update.items() if count > 0])

###
### delete zero frequency
###
c.execute("""DELETE FROM sm WHERE s_id in (%s)"""
          % ",".join('?' for s_id in delete), list(delete))



con.commit()    

#print (smt_id)
