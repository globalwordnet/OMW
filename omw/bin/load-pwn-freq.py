import sys, sqlite3

import nltk
from nltk.corpus import wordnet as pwn

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
#print(dir(pwn))

# freq[offset][lemma] = count

freq = dd(lambda: dd(int))

for ss in pwn.all_synsets():
    of = "{:08d}-{}".format(ss.offset(), ss.pos())
    for l in ss.lemmas():
        if int(l.count()):
            freq[of][l.name().replace('_', ' ')] = int(l.count()) ### don't enter count=0
            #print (of, l.name(), l.count())

sid2pwn = dict()
pwn2sid = dict()
c.execute("""SELECT ss.id, src_key 
FROM ss JOIN ili ON ili.id = ili_id 
WHERE origin_src_id=1""")
for r in c:
    sid2pwn[r[0]]= r[1]
    pwn2sid[r[1]]= r[0]
    
sense = dd(lambda: dd(int))
# sense[offset][lemma] = s_id

c.execute("""
SELECT s_id, ss_id, lemma
  FROM (SELECT w_id, canon, ss_id, s_id 
    FROM (SELECT id as s_id, ss_id, w_id FROM s) 
         JOIN w ON w_id = w.id ) 
   JOIN f ON canon = f.id WHERE lang_id=1
""" )
for (s_id, ss_id, lemma) in c:
    sense[sid2pwn[ss_id]][lemma] = s_id
    #print (s_id, ss_id, lemma, sid2pwn[ss_id])

    

## sense external link
##
## s_id, resource_id, x1=freq, x2=count
values = []
for of in freq:
    for lemma in freq[of]:
        #print (of, lemma, freq[of][lemma], sense[of][lemma])
        values.append((sense[of][lemma], 3, 
                       'freq', 1, freq[of][lemma],
                       3))
rname = 'pwn30-freq'
c.executemany("""INSERT INTO sxl (s_id, resource_id,  x1, x2, x3, u) 
VALUES (?,?, ?,?,?, ?)""", values)
# c.execute("""INSERT INTO resource(id, code, u) VALUES (?,?,?)""",
#         (3, rname, "load-pwn-freq.py"))


# if None:
#     rname = 'pwn30-freq'
#     c.execute("""INSERT INTO resource(id, code, u) VALUES (?,?,?)""",
#               (3, rname, "load-pwn-freq.py"))
#     c.executemany("""INSERT INTO resource_meta (resource_id, attr, val, u) 
#     VALUES (?,?,?,?)""",
#                   [(3, 'Name', "PWN3.0 Frequency Counts", "load-pwn-freq.py"),
#                    (3, 'License', "wordnet", "load-pwn-freq.py"),
#                    (3, 'Info', "x1 = 'freq', x2=lang_id, x3 = count", "load-pwn-freq.py")])
 
    
con.commit()      

    
    
    
    
