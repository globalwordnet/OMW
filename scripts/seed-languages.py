###
### Get all the languages currently in OMW and add them to the language list
###
### OMW 1.0 used iso639 language codes
### OMW 2.0 uses bcp47
###
###
### FIXME rerun for the Swadish list
### FIXME add all the autonyms (name in its own language)
### FIXME optionally call with a list of languages

from langcodes import standardize_tag, Language

import sqlite3, sys

shorter = {
    "Interlingua (International Auxiliary Language Association)":"Interlingua (IALA)",
    "Mandarin Chinese (simplified)":"Mandarin (简)",
    "Nepali (macrolanguage)":"Nepali (macro)",
    "Oriya (macrolanguage)":"Oriya (macro)",
    "Swahili (macrolanguage)":"Swahili (macro)",
    "Old English (ca. 450-1100)":"English, Old",
    "Ancient Greek (to 1453)":"Greek, Ancient",
    "Modern Greek (1453-)":"Greek, Modern",
    "Standard Arabic":"Arabic, Standard",
    "Tosk Albanian":"Albanian, Tosk",
    "Malaccan Creole Portuguese":"Kristang"
}


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
lids = dict()
c.execute("""SELECT id, bcp47, iso639 from lang""")
for (lid, bcp47, l3) in c:
    known[l3] = lid
    lids[bcp47] = lid

    
# OMW v1.0
langs= "eng als arb bul cmn dan ell fas fin fra heb hrv ita jpn cat eus glg spa ind zsm \
mcm nno nob pol por slv swe tha tur isl lit slk kor".split()
# wikt data
langs += "aar afr aka amh asm aze bam bel ben bod bos bre ces cor cym deu dzo epo est ewe fao ful gla gle glv guj hau hin hun hye ibo iii ina isl kal kan kat kaz khm kik kin kir kor lao lav lin lit lub lug mal mar mkd mlg mlt mon mya nbl nde nep nld oci ori orm pan pus roh ron run rus sag sin sme sna som sot srp ssw swa tam tel tgk tir ton tsn tso tur ukr urd uzb ven vie xho yor zul ang arz ast chr fry fur grc hat hbs ido kur lat ltg ltz mri nan nav rup san scn srd tat tgl tuk vol yid yue".split()

#for l3 in "eng cmn".split():
bcps=set()
for l3 in set(langs):

    if l3 in known:  ### already in
        continue 
    if l3 == 'hbs': #Serbo-Croatian
        bcp47 = 'sh'
    else:
        bcp47 = standardize_tag(l3)
    
    
    # INSERT LANG DATA (CODES AND NAMES)
    u = 'omw'
    c.execute("""INSERT INTO lang (bcp47, iso639, u)
    VALUES (?,?,?)""", (bcp47,l3,u))
    lang_id = c.lastrowid
    lids[bcp47] = lang_id
    ##print ("Inserted", lang_id,bcp47,l3,u)

for bcp in lids:
    for bcp_in in lids:
        name = Language.make(bcp).language_name(bcp_in)
        if bcp_in == bcp:
            if bcp =='ve':
                name = 'tshiVenḓa'
            elif bcp =='zsm':
                name = 'bahasa Malaysia'
            elif bcp =='id':
                name = 'bahasa Indonesia'
            elif bcp =='cmn':
                name = '中文'
            elif bcp =='mcm':
                name = 'Kristang'
                
        if name == bcp:
            continue
        ### use a shorter name if there is one
        name = shorter.get(name, name)

        
        #print(bcp, bcp_in, name, sep='\t')
        ### add if not already there
        try:
            c.execute("""INSERT INTO lang_name (lang_id, in_lang_id, name, u)
            VALUES (?,?,?,?)""", (lids[bcp], lids[bcp_in], name, u))
        except:
            'already in there'
            
con.commit()
