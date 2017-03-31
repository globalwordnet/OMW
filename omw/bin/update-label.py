##
## update the labels 
##
## id ss_id lang_id label
## 
## FIXME: not checking for confidence
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


# dbfile = "omw.db"
con = sqlite3.connect(dbfile)
c = con.cursor()
###
### get the frequency (from sm)
###
sfreq=dd(int)
c.execute("""SELECT id FROM smt WHERE tag='freq'""")
r = c.fetchone()
#print (r[0])
if r:
    c.execute("""SELECT s_id, sml_id FROM sm WHERE smt_id=?""", str(r[0]))
    for s_id, sml_id in c:
        sfreq[s_id]=sml_id
        
###
### get the senses (from sm)
###

c.execute("""
SELECT s_id, ss_id, lemma, lang_id
  FROM (SELECT w_id, canon, ss_id, s_id 
    FROM (SELECT id as s_id, ss_id, w_id FROM s) 
         JOIN w ON w_id = w.id ) 
   JOIN f ON canon = f.id
""")

senses =dd(lambda: dd(list))
#senses[ss_id][lang_id]=[(ls_id, lemma, freq), ...]
forms = dd(lambda: dd(int))
#forms[lang][word] = freq

langs=set()
eng_id=1 ### we know this :-)
for (s_id, ss_id, lemma, lang_id) in c:
    senses[ss_id][lang_id].append((s_id, lemma, sfreq[s_id]))
    forms[lang_id][lemma] += 1
    langs.add(lang_id)
    #print  (s_id, ss_id, lemma, lang_id)


###
### sort the things
### prefer frequent sense; infrequent form; short; alphabetical
   
for ss in senses:
    for l in senses[ss]:
        senses[ss][l].sort(key=lambda x: (-x[2],          ### sense freq (freq is good)
                                          forms[l][x[1]], ### uniqueness (freq is bad)  
                                          len(x[1]),  ### length (short is good)
                                          x[1]))      ### lemma (so it is the same)
#         print(ss, l, ", ".join("{} {}-{}".format(lm,f, forms[l][lm])
#                                for (s,lm,f) in senses[ss][l]))

# print("==================================")

#label[ss_id][lang_id] = label || '?????'
#
# make the labels
#

label = dd(lambda: dd(str))

lgs=sorted(langs)

values=list()
for ss in senses:
    for l in lgs:
        if senses[ss][l]:
            label[ss][l]=senses[ss][l][0][1]
        else:
            for lx in lgs:  ### start with eng and go through till you find one
                ##print ("Looking elsewhere", ss, l, lx,senses[ss][lx])
                if senses[ss][lx]:
                    label[ss][l]=senses[ss][lx][0][1]
                    break
            else:
                label[ss][l]="?????"
        values.append((ss, l,  label[ss][l]))
        #print("V", ss, l,  label[ss][l])
###
### write the labels (delete old ones first)
###
c.execute("""DELETE FROM label""")
c.executemany("""INSERT INTO label(ss_id, lang_id, label, u) 
VALUES (?,?,?,"omw")""", values)
        
con.commit()    


