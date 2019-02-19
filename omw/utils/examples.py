from collections import defaultdict as dd
import sqlite3

OMWDB = '../db/omw.db'
conn = sqlite3.connect(OMWDB)
c = conn.cursor()

# slurp pwn synsets src_id == 1

pwn = {}
c.execute("SELECT ss_id, src_key FROM ss_src WHERE src_id = ?", (1,))

for (ss_id, src_key) in c:
    pwn[ss_id] = src_key

### get English labels
label = dd(str)
c.execute("SELECT ss_id, label FROM label WHERE lang_id = ?", (1,))
for (ss_id, l) in c:
    label[ss_id] = l

### get Relation names
ssrel = {}
c.execute("SELECT id, rel FROM ssrel")
for (id, l) in c:
    ssrel[id] = l

#get sense to synset mappings
s2ss = {}
c.execute("SELECT id, ss_id FROM s")
for (id, ss) in c:
    s2ss[id] = ss
    
#get sense frequencies
ssfreq= dd(int)
c.execute("SELECT s_id, x3 FROM sxl where resource_id = 4")
for (id, f) in c:
    ssfreq[s2ss[id]] += int(f)

# get link sources
lsrc = dd(set)
c.execute("select sslink_id, val from sslink_src as s join src_meta as m on s.src_id = m.src_id where attr = 'id'")
for (sslink_id, src) in c:
    lsrc[sslink_id].add(src)

    
### get links names
links = dd(list)

c.execute("SELECT id, ss1_id, ssrel_id, ss2_id FROM sslink")
for (sslink_id, ss1_id, ssrel_id, ss2_id) in c:
    if ss1_id in pwn and ss2_id in pwn:
        links[ssrel[ssrel_id]].append((ssfreq[ss1_id] + ssfreq[ss2_id],
                                       label[ss1_id], pwn[ss1_id], ssfreq[ss1_id],
                                       label[ss2_id], pwn[ss2_id], ssfreq[ss2_id], lsrc[sslink_id]))


for link in links:
    for (freq, ss1, pwn1, f1, ss2, pwn2, f2, srcs) in sorted(links[link],reverse=True)[:40]:
        print(link, ss1, pwn1, ss2, pwn2, f1, f2, ",".join(srcs), sep='\t')

    
# for ss in list(pwn.keys())[:10]:
#     print(ss, pwn[ss], label[ss], sep='\t')
