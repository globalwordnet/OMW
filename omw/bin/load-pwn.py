#!/usr/bin/python3

# This script loads PWN in the new OMW schema
# It requires Python3 and NLTK3 installed

import sqlite3, sys, nltk
from nltk.corpus import wordnet as wn
from collections import defaultdict as dd


### ToDo: add antonyms as synset links (?)
### ToDo: examples are being loaded as synset examples, change to sense (?)

# It takes one argument: the name of the db
if (len(sys.argv) != 3):
    sys.stderr.write('usage: load-pwn.py DBFILE ILIMAP\n')
    sys.exit(1)
else:
    u =  sys.argv[0]
    dbfile = sys.argv[1]
    ilimapfile = sys.argv[2]


sys.stderr.write('Found ({}) as the new OMW database.\n'.format(dbfile))



# Verb Frames Names per Verb_id
vframe = dd(lambda: dd(str))
vframe['eng'][1] = "Something ----s"
vframe['eng'][2] = "Somebody ----s"
vframe['eng'][3] = "It is ----ing"
vframe['eng'][4] = "Something is ----ing PP"
vframe['eng'][5] = "Something ----s something Adjective/Noun"
vframe['eng'][6] = "Something ----s Adjective/Noun"
vframe['eng'][7] = "Somebody ----s Adjective"
vframe['eng'][8] = "Somebody ----s something"
vframe['eng'][9] = "Somebody ----s somebody"
vframe['eng'][10] = "Something ----s somebody"
vframe['eng'][11] = "Something ----s something"
vframe['eng'][12] = "Something ----s to somebody"
vframe['eng'][13] = "Somebody ----s on something"
vframe['eng'][14] = "Somebody ----s somebody something"
vframe['eng'][15] = "Somebody ----s something to somebody"
vframe['eng'][16] = "Somebody ----s something from somebody"
vframe['eng'][17] = "Somebody ----s somebody with something"
vframe['eng'][18] = "Somebody ----s somebody of something"
vframe['eng'][19] = "Somebody ----s something on somebody"
vframe['eng'][20] = "Somebody ----s somebody PP"
vframe['eng'][21] = "Somebody ----s something PP"
vframe['eng'][22] = "Somebody ----s PP"
vframe['eng'][23] = "Somebody's (body part) ----s"
vframe['eng'][24] = "Somebody ----s somebody to INFINITIVE"
vframe['eng'][25] = "Somebody ----s somebody INFINITIVE"
vframe['eng'][26] = "Somebody ----s that CLAUSE"
vframe['eng'][27] = "Somebody ----s to somebody"
vframe['eng'][28] = "Somebody ----s to INFINITIVE"
vframe['eng'][29] = "Somebody ----s whether INFINITIVE"
vframe['eng'][30] = "Somebody ----s somebody into V-ing something"
vframe['eng'][31] = "Somebody ----s something with something"
vframe['eng'][32] = "Somebody ----s INFINITIVE"
vframe['eng'][33] = "Somebody ----s VERB-ing"
vframe['eng'][34] = "It ----s that CLAUSE"
vframe['eng'][35] = "Something ----s INFINITIVE "

# Verb Frames Symbols per Verb_id
vframe['engsym'][1] = "☖ ~"
vframe['engsym'][2] = "☺ ~"
vframe['engsym'][3] = "It is ~ing"
vframe['engsym'][4] = "☖ is ~ing PP"
vframe['engsym'][5] = "☖ ~ ☖ Adj/N"
vframe['engsym'][6] = "☖ ~ Adj/N"
vframe['engsym'][7] = "☺ ~ Adj"
vframe['engsym'][8] = "☺ ~ ☖"
vframe['engsym'][9] = "☺ ~ ☺"
vframe['engsym'][10] = "☖ ~ ☺"
vframe['engsym'][11] = "☖ ~ ☖"
vframe['engsym'][12] = "☖ ~ to ☺"
vframe['engsym'][13] = "☺ ~ on ☖"
vframe['engsym'][14] = "☺ ~ ☺ ☖"
vframe['engsym'][15] = "☺ ~ ☖ to ☺"
vframe['engsym'][16] = "☺ ~ ☖ from ☺"
vframe['engsym'][17] = "☺ ~ ☺ with ☖"
vframe['engsym'][18] = "☺ ~ ☺ of ☖"
vframe['engsym'][19] = "☺ ~ ☖ on ☺"
vframe['engsym'][20] = "☺ ~ ☺ PP"
vframe['engsym'][21] = "☺ ~ ☖ PP"
vframe['engsym'][22] = "☺ ~ PP"
vframe['engsym'][23] = "☺'s (body part) ~"
vframe['engsym'][24] = "☺ ~ ☺ to INF"
vframe['engsym'][25] = "☺ ~ ☺ INF"
vframe['engsym'][26] = "☺ ~ that CLAUSE"
vframe['engsym'][27] = "☺ ~ to ☺"
vframe['engsym'][28] = "☺ ~ to INF"
vframe['engsym'][29] = "☺ ~ whether INF"
vframe['engsym'][30] = "☺ ~ ☺ into  Ving ☖"
vframe['engsym'][31] = "☺ ~ ☖ with ☖"
vframe['engsym'][32] = "☺ ~ INF"
vframe['engsym'][33] = "☺ ~ V-ing"
vframe['engsym'][34] = "It ~ that CLAUSE"
vframe['engsym'][35] = "☖ ~ INF "


lexnames = """0	adj.all	all adjective clusters
1	adj.pert	relational adjectives (pertainyms)
2	adv.all	all adverbs
3	noun.Tops	unique beginner for nouns
4	noun.act	nouns denoting acts or actions
5	noun.animal	nouns denoting animals
6	noun.artifact	nouns denoting man-made objects
7	noun.attribute	nouns denoting attributes of people and objects
8	noun.body	nouns denoting body parts
9	noun.cognition	nouns denoting cognitive processes and contents
10	noun.communication	nouns denoting communicative processes and contents
11	noun.event	nouns denoting natural events
12	noun.feeling	nouns denoting feelings and emotions
13	noun.food	nouns denoting foods and drinks
14	noun.group	nouns denoting groupings of people or objects
15	noun.location	nouns denoting spatial position
16	noun.motive	nouns denoting goals
17	noun.object	nouns denoting natural objects (not man-made)
18	noun.person	nouns denoting people
19	noun.phenomenon	nouns denoting natural phenomena
20	noun.plant	nouns denoting plants
21	noun.possession	nouns denoting possession and transfer of possession
22	noun.process	nouns denoting natural processes
23	noun.quantity	nouns denoting quantities and units of measure
24	noun.relation	nouns denoting relations between people or things or ideas
25	noun.shape	nouns denoting two and three dimensional shapes
26	noun.state	nouns denoting stable states of affairs
27	noun.substance	nouns denoting substances
28	noun.time	nouns denoting time and temporal relations
29	verb.body	verbs of grooming, dressing and bodily care
30	verb.change	verbs of size, temperature change, intensifying, etc.
31	verb.cognition	verbs of thinking, judging, analyzing, doubting
32	verb.communication	verbs of telling, asking, ordering, singing
33	verb.competition	verbs of fighting, athletic activities
34	verb.consumption	verbs of eating and drinking
35	verb.contact	verbs of touching, hitting, tying, digging
36	verb.creation	verbs of sewing, baking, painting, performing
37	verb.emotion	verbs of feeling
38	verb.motion	verbs of walking, flying, swimming
39	verb.perception	verbs of seeing, hearing, feeling
40	verb.possession	verbs of buying, selling, owning
41	verb.social	verbs of political and social activities and events
42	verb.stative	verbs of being, having, spatial relations
43	verb.weather	verbs of raining, snowing, thawing, thundering
44	adj.ppl	participial adjectives"""

# Short and Full Lexnames per Lexid
lexname = dd(lambda: dd(str))
for line in lexnames.split('\n'):
    lexnlst = line.split('\t')
    lexname['eng'][lexnlst[1]] = lexnlst[2]
    lexname['id'][lexnlst[1]] = lexnlst[0]


################################################################
# OPEN omw.db
################################################################
con = sqlite3.connect(dbfile)
c = con.cursor()


################################################################
# GET PWN3.0-ILI ORIGINAL MAPPING
################################################################
f = open(ilimapfile, 'r')
ili_map = dict()
for line in f:
    if line.strip() == "":
        continue
    else:
        tab = line.split('\t')
        pwn_ss = tab[1].strip()
        ili_id = tab[0][1:].strip()
        ili_map[pwn_ss] = ili_id



################################################################
# INSERT PROJECT / SRC / SRC_META DATA
################################################################

c.execute("""INSERT INTO proj (code, u)
             VALUES (?,?)""", ['pwn',u])

c.execute("""SELECT MAX(id) FROM proj""")
proj_id = c.fetchone()[0]

sys.stderr.write('PWN was attributed ({}) as proj_id.\n'.format(proj_id))


c.execute("""INSERT INTO src (proj_id, version, u)
             VALUES (?,?,?)""", [proj_id,'3.0', u])

c.execute("""SELECT MAX(id) FROM src""")
src_id = c.fetchone()[0]

sys.stderr.write('PWN30 was attributed (%s) as src_id.\n' % (src_id))


c.execute("""INSERT INTO src_meta (src_id, attr, val, u)
             VALUES (?,?,?,?)""", [src_id, 'id', 'pwn', u])

c.execute("""INSERT INTO src_meta (src_id, attr, val, u)
             VALUES (?,?,?,?)""", [src_id, 'version', '3.0', u])

c.execute("""INSERT INTO src_meta (src_id, attr, val, u)
             VALUES (?,?,?,?)""", [src_id, 'label', 'Princeton Wordnet', u])

c.execute("""INSERT INTO src_meta (src_id, attr, val, u)
             VALUES (?,?,?,?)""", [src_id, 'url', 'https://wordnet.princeton.edu', u])

c.execute("""INSERT INTO src_meta (src_id, attr, val, u)
             VALUES (?,?,?,?)""", [src_id, 'description', 'WordNet is a large, open-source, lexical database of English. Nouns, verbs, adjectives and adverbs are grouped into sets of cognitive synonyms (synsets), each expressing a distinct concept. Synsets are interlinked by means of conceptual-semantic and lexical relations.', u])


c.execute("""INSERT INTO src_meta (src_id, attr, val, u)
             VALUES (?,?,?,?)""", [src_id, 'license', 'https://wordnet.princeton.edu/wordnet/license/', u])

c.execute("""INSERT INTO src_meta (src_id, attr, val, u)
             VALUES (?,?,?,?)""", [src_id, 'language', 'en', u])

sys.stderr.write('PWN30 meta-data was added.\n')




################################################################
# INSERT (WN-EXTERNAL) RESOURCE DATA
################################################################

# FIXME!!! ADD SRC_META

c.execute("""INSERT INTO resource (code, u)
           VALUES (?,?)""", ['pwn30-lexnames',u])

c.execute("""SELECT MAX(id) FROM resource""")
lexnames_resource_id = c.fetchone()[0]


c.execute("""INSERT INTO resource (code, u)
           VALUES (?,?)""", ['pwn30-verbframes',u])

c.execute("""SELECT MAX(id) FROM resource""")
verbframes_resource_id = c.fetchone()[0]




################################################################
# INSERT LANG DATA (CODES AND NAMES)
################################################################

c.execute("""INSERT INTO lang (bcp47, iso639, u)
             VALUES (?,?,?)""", ['en','eng',u])

c.execute("""INSERT INTO lang_name (lang_id, in_lang_id, name, u)
             VALUES (1,1,'English',?)""", [u])

c.execute("""SELECT MAX(id) FROM lang""")
lang_id = c.fetchone()[0]




################################################################
# LOAD POS, SSREL, AND SREL DATA
################################################################

pos_id = dict()
c.execute("""SELECT id, tag FROM pos""")
rows = c.fetchall()
for r in rows:
    pos_id[r[1]]=r[0]

ssrel_id = dict()
c.execute("""SELECT id, rel FROM ssrel""")
rows = c.fetchall()
for r in rows:
    ssrel_id[r[1]]=r[0]

srel_id = dict()
c.execute("""SELECT id, rel FROM srel""")
rows = c.fetchall()
for r in rows:
    srel_id[r[1]]=r[0]




################################################################
# ADD ENGLISH ENTRIES
################################################################

ssid = dict()
fid = dict()
wid=dict()

ss_lemma_sense_id = dict()

def ss2of(ss):
    # FIXME!!!! 's' is getting through as the src_key on purpose!
    return "%08d-%s" % (ss.offset(), ss.pos())

for ss in wn.all_synsets():

    ili_id = int(ili_map[ss2of(ss)])

    # (1) LOAD PWN CONCEPTS AS ILI CONCEPTS
    if ss.instance_hypernyms():
        kind = 2

        c.execute("""INSERT INTO ili (id, kind_id, def, status_id,
                                      origin_src_id, src_key, u)
                     VALUES (?,?,?,?,?,?,?)
                  """, (ili_id, kind,  ss.definition(), 1,
                        src_id, ss2of(ss), u))

    else:
        kind = 1

        c.execute("""INSERT INTO ili (id, kind_id, def, status_id,
                                      origin_src_id, src_key, u)
                     VALUES (?,?,?,?,?,?,?)
                  """, (ili_id, kind,  ss.definition(), 1,
                        src_id, ss2of(ss), u))



    # (2) LOAD PWN CONCEPTS AS OMW CONCEPTS

    pos = ss.pos()
    pid = pos_id[pos.replace('s', 'a')]


    # SYNSETS
    c.execute("""INSERT INTO ss (ili_id, pos_id, u)
                 VALUES (?,?,?)
              """, (ili_id, pid, u))
    ss_id = c.lastrowid

    c.execute("""INSERT INTO ss_src (ss_id, src_id, src_key, conf, u)
                 VALUES (?,?,?,?,?)
              """, (ss_id, src_id, ss2of(ss), 1, u))

    ssid[ss2of(ss)] = ss_id


    c.execute("""INSERT INTO def (ss_id, lang_id, def, u)
                 VALUES (?,?,?,?)
              """, (ss_id, lang_id, ss.definition(), u))
    def_id = c.lastrowid

    c.execute("""INSERT INTO def_src (def_id, src_id, conf, u)
                 VALUES (?,?,?,?)
              """, (def_id, src_id, 1, u))


    # EXAMPLES
    exs = ss.examples()

    for e in exs:
        c.execute("""INSERT INTO ssexe (ss_id, lang_id, ssexe, u)
                    VALUES (?,?,?,?)
                  """, (ss_id, lang_id, e, u))
        ex_id = c.lastrowid

        c.execute("""INSERT INTO ssexe_src (ssexe_id, src_id, conf, u)
                     VALUES (?,?,?,?)
                  """, (ex_id, src_id, 1, u))



    # INSERT FORMS, WORDS (SAME) and SENSES
    for l in ss.lemmas():

        # FORMS
        form = l.name().replace('_', ' ')
        if (pid, form) in fid:
            form_id = fid[(pid, form)]
            word_id= wid
        else:
            c.execute("""INSERT INTO f (lang_id, pos_id, lemma, u)
                         VALUES (?,?,?,?)
                      """, (lang_id, pid, form, u))
            form_id = c.lastrowid
            fid[(pid, form)] = form_id

            c.execute("""INSERT INTO f_src (f_id, src_id, conf, u)
                         VALUES (?,?,?,?)
                      """, (form_id, src_id, 1, u))

            # WORDS  Only add for new form/pos pairs
            c.execute("""INSERT INTO w (canon, u)
                  VALUES (?,?) """, (form_id, u))
            word_id = c.lastrowid
            wid[(pid, form)] = word_id
            c.execute("""INSERT INTO wf_link (w_id, f_id, src_id, conf, u)
                      VALUES (?,?,?,?,?)
                       """, (word_id, form_id, src_id, 1, u))

        # SENSES
        word_id = wid[(pid, form)]
        c.execute("""INSERT INTO s (ss_id, w_id, u)
                     VALUES (?,?,?) """, (ss_id, word_id, u))
        s_id = c.lastrowid

        c.execute("""INSERT INTO s_src (s_id, src_id, conf, u)
                     VALUES (?,?,?,?) """, (s_id, src_id, 1, u))


        ss_lemma_sense_id[(ss,l)] = s_id


################################################################
# SECOND ROUND: INSERT RELATIONS
################################################################

# This now includes all relations as named in NLTK3.0
nltk_synlink_names = """also	also_sees
attribute	attributes
causes	causes
entails	entailments
hypernym	hypernyms
hyponym	hyponyms
instance_hypernym	instance_hypernyms
instance_hyponym	instance_hyponyms
holo_part	part_holonyms
mero_part	part_meronyms
similar	similar_tos
holo_substance	substance_holonyms
mero_substance	substance_meronyms
holo_member	member_holonyms
mero_member	member_meronyms
domain_topic	topic_domains
domain_region	region_domains
exemplifies	usage_domains"""
synlinks = dict()
for line in nltk_synlink_names.splitlines():
    (k, v) = line.split('\t')
    synlinks[k] = v

# list with relations not present in NLTK3.0
# but that can be inserted by finding their reverse
linkrev = dict()
linkrev['domain_topic'] = 'has_domain_topic'
linkrev['exemplifies'] = 'is_exemplified_by'
linkrev['domain_region'] = 'has_domain_region'

nltk_senslink_names = """antonym	antonyms
pertainym	pertainyms
derivation	derivationally_related_forms"""
senslinks = dict()
for line in nltk_senslink_names.splitlines():
    (k, v) = line.split('\t')
    senslinks[k] = v


for ss in wn.all_synsets():

    pos = ss.pos()
    pid = pos_id[pos.replace('s', 'a')]

    # SSREL
    for r in synlinks.keys():
        for ss2 in getattr(ss, synlinks[r])():

            c.execute("""INSERT INTO sslink (ss1_id, ssrel_id, ss2_id, u)
                         VALUES (?,?,?,?)""",
                      (ssid[ss2of(ss)], ssrel_id[r], ssid[ss2of(ss2)], u))
            sslink_id = c.lastrowid

            c.execute("""INSERT INTO sslink_src (sslink_id, src_id, conf, lang_id, u)
                         VALUES (?,?,?,?,?)""",
                      (sslink_id, src_id, 1, lang_id, u))


            if r in linkrev.keys(): # insert the reverse relation

                c.execute("""INSERT INTO sslink (ss1_id, ssrel_id, ss2_id, u)
                             VALUES (?,?,?,?)""",
                          (ssid[ss2of(ss2)], ssrel_id[linkrev[r]], ssid[ss2of(ss)], u))
                sslink_id = c.lastrowid

                c.execute("""INSERT INTO sslink_src (sslink_id, src_id, conf, lang_id, u)
                             VALUES (?,?,?,?,?)""",
                          (sslink_id, src_id, 1, lang_id, u))


    # SS LEXNAMES
    lxn = ss.lexname()

    c.execute("""INSERT INTO ssxl (ss_id, resource_id, x1, x2, x3, u)
                 VALUES (?,?,?,?,?,?)
              """, (ssid[ss2of(ss)], lexnames_resource_id, lexname['id'][lxn],
                    lxn, lexname['eng'][lxn], u))

    # SS VERBFRAMES
    sframes = ss.frame_ids()
    for frame in sframes:

        c.execute("""INSERT INTO ssxl (ss_id, resource_id, x1, x2, x3, u)
                     VALUES (?,?,?,?,?,?)
                  """, (ssid[ss2of(ss)], verbframes_resource_id, frame,
                        vframe['eng'][frame], vframe['engsym'][frame], u))



    # SENSE LINKS
    for l1 in ss.lemmas():
        s1_id = ss_lemma_sense_id[(ss,l1)]

        lframeids = l1.frame_ids() # lemma frames

        for frame in lframeids:

            c.execute("""INSERT INTO sxl (s_id, resource_id, x1, x2, x3, u)
                         VALUES (?,?,?,?,?,?)
                      """, (s1_id, verbframes_resource_id, frame,
                            vframe['eng'][frame], vframe['engsym'][frame], u))


        for r in senslinks:
            for l2 in getattr(l1, senslinks[r])():

                s2_id = ss_lemma_sense_id[(l2.synset(),l2)]

                c.execute("""INSERT INTO slink (s1_id, srel_id, s2_id, u)
                             VALUES (?,?,?,?)""",
                          (s1_id, srel_id[r], s2_id, u))
                slink_id = c.lastrowid

                c.execute("""INSERT INTO slink_src (slink_id, src_id, conf, u)
                             VALUES (?,?,?,?)""",
                          (slink_id, src_id, 1, u))




con.commit()
con.close()

sys.stderr.write('Loaded PWN30!')
