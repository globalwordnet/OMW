#!/usr/bin/python3

import sqlite3, sys

# It takes one argument: the name of the db
if (len(sys.argv) < 2):
    sys.stderr.write('You need to give the name of the DB\n')
    sys.exit(1)
else:
    u =  sys.argv[0]
    dbfile = sys.argv[1]

tags = {
    "meta": "other meta information",  
    "morph": "morphological information",  # like sg, pl
    "orth": "orthographical information",
    "trans": "transcription/romanization"
}
labels = {
    # morph
    "sg": "singular",  
    "pl": "plural",
    # trans
    "pinyin": "pinyin, no tones",
    "pīnyīn": "pinyin, tones as accents",
    "pin1yin1": "pinyin, tones as numbers",
    "ascii": "ascii transliteration",
    # meta
    "f": "female form",
}
    
################################################################
# CONNECT TO DB
################################################################
con = sqlite3.connect(dbfile)
c = con.cursor()


################################################################
# INSERT POS DATA (CODES AND NAMES)
################################################################

for (tag, name) in tags.items():
    c.execute("""INSERT INTO fmt (tag, name, u) 
                 VALUES (?,?,?)""", (tag, name, u))

for (label, name) in labels.items():
    c.execute("""INSERT INTO fml (label, name, u) 
                 VALUES (?,?,?)""", (label, name, u))



con.commit()
con.close()
sys.stderr.write('Loaded form meta-data tgs ({})\n'.format(dbfile))
