import sqlite3
import sys, time

dbfile = "omw.db"
con = sqlite3.connect(dbfile)
curs = con.cursor()

commandlist = [
("""PRAGMA foreign_keys = 1;""",
 """Activating foreign key constraints"""),

("""INSERT INTO active_user (user_id) 
    VALUES ('test-user-deleter');""", 
 """Inserting active user"""),

# TESTING lang TABLE

("""INSERT INTO lang (bcp47, iso639, u) 
    VALUES ('en', 'eng', 'test-user');""", 
 """Inserting in lang table"""),

("""UPDATE lang
    SET bcp47 = 'enGLOBAL', u='test-user2' 
    WHERE bcp47 = 'en';""", 
 """Updating in lang table"""),

# TESTING lang_name TABLE

("""INSERT INTO lang_name (lang_id, in_lang_id, name, u) 
    VALUES (1, 1, 'English', 'test-user');""", 
 """Inserting in lang_name table"""),

("""UPDATE lang_name
    SET name = 'ENGLISH-GLOBAL', u='test-user2' 
    WHERE name = 'English';""", 
 """Updating in lang_name table"""),



# TESTING proj TABLE
("""INSERT INTO proj (code, u)
    VALUES ('ntutest', 'test-user');""",
 """Inserting in proj table"""),

("""UPDATE proj
    SET code = 'ntutest2', u='test-user2'
    WHERE code = 'ntutest';""",
 """Updating in proj table"""),


# TESTING scr TABLE
("""INSERT INTO src (proj_id, version, u)
    VALUES (1, '3.0', 'test-user');""",
 """Inserting in src table"""),

("""UPDATE src
    SET version = '3.2', u='test-user2'
    WHERE version = '3.0';""",
 """Updating in src table"""),


# TESTING scr_meta TABLE

("""INSERT INTO src_meta (src_id, attr, val, u) 
    VALUES (1, 'attr-test','val-test', 'test-user');""", 
 """Inserting in src_meta table"""),

("""UPDATE src_meta 
    SET attr = 'attr-test2', u='test-user2' WHERE attr = 'attr-test';""", 
 """Updating in src_meta table"""),

("""DELETE FROM src_meta WHERE attr = 'attr-test2';""", 
 """Deleting in src_meta table"""),

# TESTING pos TABLE

("""INSERT INTO pos (tag, def, u) 
    VALUES ('n', 'noun','test-user');""", 
 """Inserting in pos table"""),

("""UPDATE pos 
    SET def = 'Noun', u='test-user2' WHERE tag = 'n';""", 
 """Updating in pos table"""),

# TESTING ssrel TABLE

("""INSERT INTO ssrel (rel, def, u) 
    VALUES ('hypo', 'hyponym','test-user');""", 
 """Inserting in ssrel table"""),

("""UPDATE ssrel
    SET def = 'Hyponymity', u='test-user2' WHERE rel = 'hypo';""", 
 """Updating in ssrel table"""),

# TESTING srel TABLE

("""INSERT INTO srel (rel, def, u) 
    VALUES ('derv', 'derivation','test-user');""", 
 """Inserting in srel table"""),

("""UPDATE srel
    SET def = 'Derivational Link', u='test-user2' WHERE rel = 'derv';""", 
 """Updating in srel table"""),

# TESTING ss TABLE

("""INSERT INTO ss (ili_id, pos_id, u) 
    VALUES (1, 1, 'test-user');""", 
 """Inserting in ss table"""),

("""UPDATE ss
    SET ili_id = 2, u='test-user2' WHERE id = 1;""", 
 """Updating in ss table"""),

# TESTING ss_src TABLE

("""INSERT INTO ss_src (ss_id, src_id, src_key, conf, u) 
    VALUES (1, 1,'0000000-n', 1, 'test-user');""", 
 """Inserting in ss_src table"""),

("""UPDATE ss_src
    SET conf = 2, u='test-user2' WHERE ss_id = 1;""", 
 """Updating in ss_src table"""),

# TESTING f TABLE

("""INSERT INTO f (lang_id, pos_id, lemma, u) 
    VALUES (1, 1, 'music', 'test-user');""", 
 """Inserting in f table"""),

("""UPDATE f
    SET lemma = 'miusic', u='test-user2' WHERE lemma = 'music';""", 
 """Updating in f table"""),

# TESTING f_src TABLE

("""INSERT INTO f_src (f_id, src_id, conf, u) 
    VALUES (1, 1, 1, 'test-user');""", 
 """Inserting in f_src table"""),

("""UPDATE f_src
    SET conf = 2, u='test-user2' WHERE f_id = 1;""", 
 """Updating in f_src table"""),

# TESTING fmt TABLE

("""INSERT INTO fmt (tag, name, u) 
    VALUES ('freq', 'frequency', 'test-user');""", 
 """Inserting in fmt table"""),

("""UPDATE fmt
    SET name = 'Frequency-corrected', u='test-user2' WHERE tag = 'freq';""", 
 """Updating in fmt table"""),

# TESTING fml TABLE

("""INSERT INTO fml (label, name, u) 
    VALUES ('kata', 'katakana', 'test-user');""", 
 """Inserting in fml table"""),

("""UPDATE fml
    SET name = 'Katakana Ortography', u='test-user2' WHERE label = 'kata';""", 
 """Updating in fml table"""),

# TESTING fm TABLE

("""INSERT INTO fm (f_id, fmt_id, fml_id, u) 
    VALUES (1, 1, 33, 'test-user');""", 
 """Inserting in fm table"""),

("""UPDATE fm
    SET fml_id = 99, u='test-user2' WHERE f_id = 1;""", 
 """Updating in fm table"""),

# TESTING fm_src TABLE

("""INSERT INTO fm_src (fm_id, src_id, conf, u) 
    VALUES (1, 1, 1, 'test-user');""", 
 """Inserting in fm_src table"""),

("""UPDATE fm_src
    SET conf = 2, u='test-user2' WHERE fm_id = 1;""", 
 """Updating in fm_src table"""),

# TESTING w TABLE

("""INSERT INTO w (canon, u) 
    VALUES (1, 'test-user');""", 
 """Inserting in w table"""),

("""UPDATE w
    SET t = 2, u='test-user2' WHERE id = 1;""", 
 """Updating in w table"""),

# TESTING wf_link TABLE

("""INSERT INTO wf_link (w_id, f_id, src_id, conf, u) 
    VALUES (1, 1, 1, 1, 'test-user');""", 
 """Inserting in wf_link table"""),

("""UPDATE wf_link
    SET conf = 2, u='test-user2' WHERE w_id = 1 AND f_id = 1;""", 
 """Updating in wf_link table"""),

# TESTING s TABLE

("""INSERT INTO s (ss_id, w_id, u) 
    VALUES (1, 1, 'test-user');""", 
 """Inserting in s table"""),

("""UPDATE s
    SET t = 2, u='test-user2' WHERE id = 1;""", 
 """Updating in s table"""),

# TESTING s_src TABLE

("""INSERT INTO s_src (s_id, src_id, conf, u) 
    VALUES (1, 1, 1, 'test-user');""", 
 """Inserting in s_src table"""),

("""UPDATE s_src
    SET conf = 2, u='test-user2' WHERE s_id = 1;""", 
 """Updating in s_src table"""),

# TESTING smt TABLE

("""INSERT INTO smt (tag, name, u) 
    VALUES ('freq', 'frequency', 'test-user');""", 
 """Inserting in smt table"""),

("""UPDATE smt
    SET name = 'Frequency-corrected', u='test-user2' WHERE tag = 'freq';""", 
 """Updating in smt table"""),

# TESTING sml TABLE

("""INSERT INTO sml (label, name, u) 
    VALUES ('kata', 'katakana', 'test-user');""", 
 """Inserting in sml table"""),

("""UPDATE sml
    SET name = 'Katakana Ortography', u='test-user2' WHERE label = 'kata';""", 
 """Updating in sml table"""),

# TESTING sm TABLE

("""INSERT INTO sm (s_id, smt_id, sml_id, u) 
    VALUES (1, 1, 30, 'test-user');""", 
 """Inserting in sm table"""),

("""UPDATE sm
    SET sml_id = 66, u='test-user2' WHERE s_id = 1;""", 
 """Updating in sm table"""),

# TESTING s_src TABLE

("""INSERT INTO sm_src (sm_id, src_id, conf, u) 
    VALUES (1, 1, 1, 'test-user');""", 
 """Inserting in sm_src table"""),

("""UPDATE sm_src
    SET conf = 2, u='test-user2' WHERE sm_id = 1;""", 
 """Updating in sm_src table"""),

# TESTING def TABLE

("""INSERT INTO def (ss_id, lang_id, def, u) 
    VALUES (1, 1, 'definition-example','test-user');""", 
 """Inserting in def table"""),

("""UPDATE def
    SET def = 'new-def', u='test-user2' WHERE id = 1;""", 
 """Updating in def table"""),

# TESTING def_src TABLE

("""INSERT INTO def_src (def_id, src_id, conf, u) 
    VALUES (1, 1, 1, 'test-user');""", 
 """Inserting in def_src table"""),

("""UPDATE def_src
    SET conf = 2, u='test-user2' WHERE def_id = 1;""", 
 """Updating in def_src table"""),


# TESTING (sense) exe TABLE

("""INSERT INTO exe (s_id, exe, u) 
    VALUES (1, 'example','test-user');""", 
 """Inserting in exe table"""),

("""UPDATE exe
    SET exe = 'new-ex', u='test-user2' WHERE id = 1;""", 
 """Updating in exe table"""),

# TESTING (sense) exe_src TABLE

("""INSERT INTO exe_src (exe_id, src_id, conf, u) 
    VALUES (1, 1, 1, 'test-user');""", 
 """Inserting in exe_src table"""),

("""UPDATE exe_src
    SET conf = 2, u='test-user2' WHERE exe_id = 1;""", 
 """Updating in exe_src table"""),


# TESTING ssexe TABLE

("""INSERT INTO ssexe (ss_id, lang_id, ssexe, u) 
    VALUES (1, 1, 'example','test-user');""", 
 """Inserting in ssexe table"""),

("""UPDATE ssexe
    SET ssexe = 'new-ex', u='test-user2' WHERE id = 1;""", 
 """Updating in ssexe table"""),

# TESTING ssexe_src TABLE

("""INSERT INTO ssexe_src (ssexe_id, src_id, conf, u) 
    VALUES (1, 1, 1, 'test-user');""", 
 """Inserting in ssexe_src table"""),

("""UPDATE ssexe_src
    SET conf = 2, u='test-user2' WHERE ssexe_id = 1;""", 
 """Updating in ssexe_src table"""),

# TESTING sslink TABLE

("""INSERT INTO sslink (ss1_id, ssrel_id, ss2_id, u) 
    VALUES (1, 1, 1, 'test-user');""", 
 """Inserting in sslink table"""),

("""UPDATE sslink
    SET t = 2, u='test-user2' WHERE id = 1;""", 
 """Updating in sslink table"""),

# TESTING sslink_src TABLE

("""INSERT INTO sslink_src (sslink_id, src_id, conf, lang_id, u) 
    VALUES (1, 1, 1, 1, 'test-user');""", 
 """Inserting in sslink_src table"""),

("""UPDATE sslink_src
    SET conf = 2, u='test-user2' WHERE sslink_id = 1;""", 
 """Updating in sslink_src table"""),

# TESTING slink TABLE

("""INSERT INTO slink (s1_id, srel_id, s2_id, u) 
    VALUES (1, 1, 1, 'test-user');""", 
 """Inserting in slink table"""),

("""UPDATE slink
    SET t = 2, u='test-user2' WHERE id = 1;""", 
 """Updating in slink table"""),

# TESTING slink_src TABLE

("""INSERT INTO slink_src (slink_id, src_id, conf, u) 
    VALUES (1, 1, 1, 'test-user');""", 
 """Inserting in slink_src table"""),

("""UPDATE slink_src
    SET conf = 2, u='test-user2' WHERE slink_id = 1;""", 
 """Updating in slink_src table"""),

# TESTING ssslink TABLE

("""INSERT INTO ssslink (s_id, srel_id, ss_id, u) 
    VALUES (1, 1, 1, 'test-user');""", 
 """Inserting in ssslink table"""),

("""UPDATE ssslink
    SET t = 2, u='test-user2' WHERE id = 1;""", 
 """Updating in ssslink table"""),

# TESTING ssslink_src TABLE

("""INSERT INTO ssslink_src (ssslink_id, src_id, conf, lang_id, u) 
    VALUES (1, 1, 1, 1, 'test-user');""", 
 """Inserting in ssslink_src table"""),

("""UPDATE ssslink_src
    SET conf = 2, u='test-user2' WHERE ssslink_id = 1;""", 
 """Updating in ssslink_src table"""),

# TESTING resource TABLE

("""INSERT INTO resource (code, u) 
    VALUES ('ntutest', 'test-user');""", 
 """Inserting in resource table"""),

("""UPDATE resource 
    SET code = 'ntutest2', u='test-user2' 
    WHERE code = 'ntutest';""", 
 """Updating in resource table"""),

# TESTING resource_meta TABLE

("""INSERT INTO resource_meta (resource_id, attr, val, u) 
    VALUES (1, 'attr-test','val-test', 'test-user');""", 
 """Inserting in src_meta table"""),

("""UPDATE resource_meta 
    SET attr = 'attr-test2', u='test-user2' WHERE attr='attr-test';""", 
 """Updating in resource_meta table"""),

("""DELETE FROM resource_meta;""", 
 """Deleting in resource_meta table"""),

# TESTING ssxl TABLE

("""INSERT INTO ssxl (ss_id, resource_id, x1, x2, x3, u) 
    VALUES (1, 1, 'test1', 'test2', 'test3', 'test-user');""", 
 """Inserting in ssxl table"""),

("""UPDATE ssxl 
    SET x1 = 'ntutest2', u='test-user2' 
    WHERE id = 1;""", 
 """Updating in ssxl table"""),

# TESTING sxl TABLE

("""INSERT INTO sxl (s_id, resource_id, x1, x2, x3, u) 
    VALUES (1, 1, 'test1', 'test2', 'test3', 'test-user');""", 
 """Inserting in ssxl table"""),

("""UPDATE ssxl 
    SET x1 = 'ntutest2', u='test-user2' 
    WHERE id = 1;""", 
 """Updating in ssxl table"""),

# TESTING ss_com TABLE

("""INSERT INTO ss_com (ss_id, com, u) 
    VALUES (1, 'test3', 'test-user');""", 
 """Inserting in ss_com table"""),

("""UPDATE ss_com 
    SET com = 'ntutest2', u='test-user2' 
    WHERE id = 1;""", 
 """Updating in ss_com table"""),


# DELETING THINGS (IN THE RIGHT ORDER)

("""DELETE FROM ss_com;""", 
 """Deleting in ss_com table"""),

("""DELETE FROM sxl;""", 
 """Deleting in sxl table"""),

("""DELETE FROM ssxl;""", 
 """Deleting in ssxl table"""),

("""DELETE FROM resource;""", 
 """Deleting in resource table"""),

("""DELETE FROM ssslink_src;""", 
 """Deleting in ssslink_src table"""),

("""DELETE FROM ssslink;""", 
 """Deleting in ssslink table"""),

("""DELETE FROM slink_src;""", 
 """Deleting in slink_src table"""),

("""DELETE FROM slink;""", 
 """Deleting in slink table"""),

("""DELETE FROM sslink_src;""", 
 """Deleting in sslink_src table"""),

("""DELETE FROM sslink;""", 
 """Deleting in sslink table"""),

("""DELETE FROM exe_src;""", 
 """Deleting in exe_src table"""),

("""DELETE FROM exe;""", 
 """Deleting in exe table"""),

("""DELETE FROM ssexe_src;""", 
 """Deleting in ssexe_src table"""),

("""DELETE FROM ssexe;""", 
 """Deleting in ssexe table"""),

("""DELETE FROM def_src;""", 
 """Deleting in def_src table"""),

("""DELETE FROM def;""", 
 """Deleting in def table"""),

("""DELETE FROM sm_src;""", 
 """Deleting in sm_src table"""),

("""DELETE FROM sm;""", 
 """Deleting in sm table"""),

("""DELETE FROM smt;""", 
 """Deleting in smt table"""),

("""DELETE FROM sml;""", 
 """Deleting in sml table"""),

("""DELETE FROM s_src;""", 
 """Deleting in s_src table"""),

("""DELETE FROM s;""", 
 """Deleting in s table"""),

("""DELETE FROM wf_link;""", 
 """Deleting in wf_link table"""),

("""DELETE FROM w;""", 
 """Deleting in w table"""),

("""DELETE FROM fm_src;""", 
 """Deleting in fm_src table"""),

("""DELETE FROM fm;""", 
 """Deleting in fm table"""),

("""DELETE FROM fml;""", 
 """Deleting in fml table"""),

("""DELETE FROM fmt;""", 
 """Deleting in fmt table"""),

("""DELETE FROM f_src;""", 
 """Deleting in f_src table"""),

("""DELETE FROM f;""", 
 """Deleting in f table"""),

("""DELETE FROM ss_src;""", 
 """Deleting in ss_src table"""),

("""DELETE FROM ss;""", 
 """Deleting in ss table"""),

("""DELETE FROM ssrel;""", 
 """Deleting in ssrel table"""),

("""DELETE FROM pos;""", 
 """Deleting in pos table"""),

("""DELETE FROM lang_name;""", 
 """Deleting in lang_name table"""),

("""DELETE FROM lang;""", 
 """Deleting in lang table"""),

("""DELETE FROM src;""", 
 """Deleting in src table"""),

("""DELETE FROM active_user;""", 
 """Deleting active user""")


]




failedcommands = []
for command in commandlist:
        try:
                time.sleep(0.5)
                curs.execute(command[0])
                print("PASSED: {} ".format(command[1]))
        except:
            failedcommands.append(command[0])
            print("FAILED: <<<< {} >>>>  !!!".format(command[1]))

if failedcommands == []:
    print("")
    print("Congratulations, it seems everything went well!")

con.commit()
con.close()
