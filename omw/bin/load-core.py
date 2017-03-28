###
### Read the core data
### Map it to ili
### load it into the xlink table
###
import sys, sqlite3

# It takes one argument: the name of the db
if (len(sys.argv) < 2):
    sys.stderr.write('You need to give the name of the DB\n')
    sys.exit(1)
else:
    uname =  sys.argv[0]
    dbfile = sys.argv[1]

con = sqlite3.connect(dbfile)
c = con.cursor()


################################################################
# GET core data
################################################################
f = open('wn30-core-synsets.tab', 'r')
core = set()
icore=set()
for line in f:
    if line.strip() == "":
        continue
    else:
        core.add(line.strip())

################################################################
# GET PWN3.0-ILI ORIGINAL MAPPING
################################################################
f = open('ili-map.tab', 'r')
ili_map = dict()
ili2ss=dict()
for line in f:
    if line.strip() == "":
        continue
    else:
        tab = line.split('\t')
        pwn_ss = tab[1].strip()
        ili_id = tab[0][1:].strip()
        #ili_map[pwn_ss.replace('-s', '-a')] = ili_id
        ili2ss[int(ili_id)] = pwn_ss.replace('-s', '-a')
        #print(ili_id, pwn_ss.replace('-s', '-a'),  pwn_ss.replace('-s', '-a') in core)
     
################################################################
# Enter core data
################################################################
rname='core'
#uname='load-core.py'
values=list()

c.execute('select id, ili_id from ss')
for (ss_id, ili_id) in c:
    #print(ss_id, ili_id)
    if ili_id in ili2ss and ili2ss[ili_id] in core:
        values.append((ss_id, ili_id, ili2ss[ili_id]))
        #print(ss_id, ili_id, ili2ss[ili_id])
        
c.execute('select id from resource where code = ?', (rname,))
r = c.fetchone()
if r:
    ### core already exists
    rid = r[0]
else:
    ### enter the resource
    c.execute("""INSERT INTO resource(code, u) VALUES (?,?)""",
              (rname, uname))
    rid = c.lastrowid
    ### enter the resource meta-data
    c.executemany("""INSERT INTO resource_meta (resource_id, attr, val, u) 
    VALUES (?,?,?,?)""",
                  [(rid, 'Name', "Core Synsets", uname),
                   (rid, 'Info', "x1 = 'iliid', x2='pwn-3.0 key'", uname)])

    ### enter the data
    c.executemany("""INSERT INTO ssxl (ss_id, resource_id,  x1, x2, u) 
    VALUES (?, ?, ?,?, ?)""", [(v[0], rid, v[1], v[2], uname) for v in values])

con.commit()
con.close()
