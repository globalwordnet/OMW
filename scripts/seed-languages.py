###
### Get all the languages currently in OMW and add them to the language list
###
### FIXME --- rerun for the Swadesh list

### sudo pip3 install iso-639
from iso639 import languages

import sqlite3, sys

# It takes one argument: the name of the db
if (len(sys.argv) < 2):
    sys.stderr.write('You need to give the name of the DB\n')
    sys.exit(1)
else:
    u =  sys.argv[0]
    dbfile = sys.argv[1]

con = sqlite3.connect(dbfile)
c = con.cursor()


known = dict()
c.execute("""SELECT id, iso639 from lang""")
for (lid, l3) in c:
    known[l3] = lid

#for l3 in "eng cmn".split():
for l3 in "eng als arb bul cmn dan ell fas fin fra heb hrv ita jpn cat eus glg spa ind zsm nno nob pol por slv swe tha tur".split():
 # aar afr aka amh asm aze bam bel ben bod bos bre ces cor cym deu dzo epo est ewe fao ful gla gle glv guj hau hin hun hye ibo iii ina isl kal kan kat kaz khm kik kin kir kor lao lav lin lit lub lug mal mar mkd mlg mlt mon mya nbl nde nep nld oci ori orm pan pus roh ron run rus sag sin slk sme sna som sot srp ssw swa tam tel tgk tir ton tsn tso tur ukr urd uzb ven vie xho yor zul ang arz ast chr fry fur grc hat hbs ido kur lat ltg ltz mri nan nav rup san scn srd tat tgl tuk vol yid yue".split():
    if l3 in known:  ### already in
        continue 

    l = languages.get(part3=l3)
    
    if l.part1:  ### use the two letter code if it exists
        bcp47 = l.part1
    else:
        bcp47 = l3

    
    # INSERT LANG DATA (CODES AND NAMES)
    u = 'omw'
    c.execute("""INSERT INTO lang (bcp47, iso639, u)
                  VALUES (?,?,?)""", (bcp47,l3,u))

    c.execute("""SELECT MAX(id) FROM lang""")
    lang_id = c.fetchone()[0]

    c.execute("""INSERT INTO lang_name (lang_id, in_lang_id, name, u)
    VALUES (?,?,?,?)""", (lang_id, known['eng'], l.name, u))

con.commit()
