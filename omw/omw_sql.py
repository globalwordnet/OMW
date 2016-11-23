#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, sqlite3
from flask import Flask, current_app, g
from collections import defaultdict as dd
from collections import namedtuple as nt
from common_sql import *

#ntsense=namedtuple('Sense', ['lemma', 'y'], verbose=True)

    
app = Flask(__name__)
with app.app_context():

    def fetch_langs():
        lang_id = dd(lambda: dd())
        lang_code = dd(lambda: dd())
        for r in query_omw("""SELECT id, bcp47, iso639, in_lang_id, name
                             FROM lang JOIN lang_name
                             ON id = lang_id"""):
            lang_id[r['id']]['bcp47'] = r['bcp47']
            lang_id[r['id']]['iso639'] = r['iso639']
            lang_id[r['id']][r['in_lang_id']] = r['name']
            lang_code['code'][r['bcp47']] = r['id']
            lang_code['code'][r['iso639']] = r['id']
        return lang_id, lang_code

    def fetch_key_bcp_lang_code(lang):
        """ There should be only one id for either lang code """
        for r in query_omw("""SELECT id
                              FROM lang
                              WHERE (bcp47 = ?)""", [lang]):
            return r['id']

    def fetch_proj():
        proj_id = dict()
        for r in query_omw("""SELECT id, code FROM proj"""):
            proj_id[r['id']]=r['code']
        return proj_id

    def insert_new_project(code, u):
        " Adds a new project to the system "
        try:
            proj_code = code.strip() if code else code
            write_omw("""INSERT INTO proj (code, u)
                         VALUES (?,?) """, [proj_code, u])
            return True
        except:
            return False

    def f_proj_id_by_code(code):
        for r in query_omw("""SELECT id, code
                              FROM proj
                              WHERE code = ?""", [code]):
            return r['id']


    def fetch_src():
        proj_id = fetch_proj()
        src_id = dict()
        for r in query_omw("""SELECT id, proj_id, version FROM src"""):
            src_id[r['id']]=(proj_id[r['proj_id']],r['version'])
        return src_id

    def insert_src(proj_id, version, u):
        return write_omw("""INSERT INTO src (proj_id, version, u)
                            VALUES (?,?,?)""",
                         [proj_id, version, u])

    def f_src_id_by_proj_id_ver(proj_id, version):
        for r in query_omw("""SELECT id, proj_id, version
                              FROM src
                              WHERE proj_id = ? AND version = ?""",
                           [proj_id, version]):

            return r['id']
        
    def f_src_id_by_proj_ver(proj, version):
        for r in query_omw("""SELECT src.id 
                              FROM src JOIN proj
                              ON src.proj_id=proj.id 
                              WHERE proj.code= ? AND src.version = ?""",
                           [proj, version]):
            return r['id']   

    def fetch_src_meta():
        src_meta = dd(lambda:  dd(str))
        for r in query_omw("""SELECT src_id, attr, val, u, t FROM src_meta"""):
             src_meta[r['src_id']][r['attr']] = r['val']
             #src_meta_id[r['src_id']].append(r)
        return src_meta

    def fetch_src_id_stats(src_id):
        src_id_stats=dd(int)
        for r in query_omw("""SELECT count(distinct s.ss_id),
        count(distinct s.w_id), count(distinct s.id)
        FROM s JOIN s_src ON s.id=s_src.s_id 
        WHERE s_src.Src_id=?""", [src_id]):
             src_id_stats['synsets'] = r['count(distinct s.ss_id)']
             src_id_stats['words'] = r['count(distinct s.w_id)']
             src_id_stats['senses'] = r['count(distinct s.id)']
             return src_id_stats
        
    def fetch_src_for_s_id(s_ids):
        """return a dict of lists of (src_ids, conf)  per sense id
           src_id[s_id] = [(src_id, conf), ... ]
        """
        src_sid = dd(list)
        for r in query_omw("""SELECT s_id, src_id, conf 
        FROM s_src WHERE s_id in (%s)""" % qs(s_ids), s_ids):
            src_sid[r['s_id']].append((r['src_id'], r['conf']))
        return src_sid

         
    def insert_src_meta(src_id, attr, val, u):
        return write_omw("""INSERT INTO src_meta (src_id, attr, val, u)
                            VALUES (?,?,?,?)""",
                         [src_id, attr, val, u])

    def blk_insert_src_meta(tuple_list):
        """ tupple_list must of of format [(src_id, attr, val, u), ...] """
        return blk_write_omw("""INSERT INTO src_meta (src_id, attr, val, u)
                                VALUES (?,?,?,?)""", tuple_list)

    def fetch_kind():
        kind_id = dict()
        for r in query_omw("""SELECT id, kind FROM kind"""):
            kind_id[r['id']]=r['kind']
        return kind_id

    def fetch_status():
        status_id = dict()
        for r in query_omw("""SELECT id, status FROM status"""):
            status_id[r['id']]=r['status']
        return status_id


    def fetch_max_ili_id():
        for r in query_omw("""SELECT MAX(id) FROM ili"""):
            return r['MAX(id)']

    def fetch_max_ss_id():
        for r in query_omw("""SELECT MAX(id) FROM ss"""):
            return r['MAX(id)']

    def fetch_max_def_id():
        for r in query_omw("""SELECT MAX(id) FROM def"""):
            return r['MAX(id)']

    def fetch_max_ssexe_id():
        for r in query_omw("""SELECT MAX(id) FROM ssexe"""):
            return r['MAX(id)']

    def fetch_max_sslink_id():
        for r in query_omw("""SELECT MAX(id) FROM sslink"""):
            return r['MAX(id)']

    def fetch_max_f_id():
        for r in query_omw("""SELECT MAX(id) FROM f"""):
            return r['MAX(id)']

    def fetch_max_w_id():
        for r in query_omw("""SELECT MAX(id) FROM w"""):
            return r['MAX(id)']

    def fetch_max_s_id():
        for r in query_omw("""SELECT MAX(id) FROM s"""):
            return r['MAX(id)']


    def insert_into_ili(kind, definition, status, src, key, u):
        return write_omw("""INSERT INTO ili
                           (kind_id, def, status_id, origin_src_id, src_key, u)
                           VALUES (?,?,?,?,?,?)""",
                 [kind, definition, status, src, key, u])

    def blk_insert_into_ili(tuple_list):
        return blk_write_omw("""INSERT INTO ili
                                (id, kind_id, def, status_id, origin_src_id, src_key, u)
                                VALUES (?,?,?,?,?,?,?)""", tuple_list)


    def fetch_rate_id(ili_ids, u=None):
        """
        This function takes a list of ili ids and, optionally a username.
        It returns a dictionary with the ratings filtered by the ids and,
        if provided, for that specific user.
        """
        rating = dd(list)
        ili_list = (",".join("?" for s in ili_ids), ili_ids)
        if u:
            # sys.stderr.write('\n USER MODE \n') #TEST
            for r in query_omw("""SELECT id, ili_id, rating, u, t
                                  FROM ili_rating
                                  WHERE ili_id in ({})
                                  AND   u = ?""".format(ili_list[0]),
                               ili_list[1]+[u]):
                rating[r['ili_id']].append((r['rating'], r['u'], r['t']))
        else:
            # sys.stderr.write('\n NON USER MODE \n') #TEST
            for r in query_omw("""SELECT id, ili_id, rating, u, t
                                  FROM ili_rating
                                  WHERE ili_id in ({})
                               """.format(ili_list[0]),
                               ili_list[1]):
                rating[r['ili_id']].append((r['rating'], r['u'], r['t']))

        return rating

    def f_rate_summary(ili_ids):
        """
        This function takes a list of ili ids and returns a dictionary with the
        cumulative ratings filtered by the ids.
        """
        counts = dd(lambda: dd(int))
        rates = fetch_rate_id(ili_ids)
        up_who = dd(list)
        down_who = dd(list)
        for key, value in rates.items():
            for (r, u, t) in rates[key]:
                if r == 1:
                    counts[int(key)]['up'] += 1
                    up_who[int(key)].append(u)
                elif r == -1:
                    counts[int(key)]['down'] += 1
                    down_who[int(key)].append(u)

        return counts, up_who, down_who



    def rate_ili_id(ili_id, rate, u):
        """
        This function is used to give a +1 or -1 rating to ili ids. It only updates
        these values when necessary, overwritting the previous rating if it was
        different. Returns True on update and None if no changes were necessary.
        """
        ili_id = int(ili_id)
        rating = fetch_rate_id([ili_id], u)

        if ili_id in rating:

            if rating[ili_id][0][0] == rate:
                return None
            else:
                write_omw("""UPDATE ili_rating
                             SET rating = ?
                             WHERE ili_id = ?
                             AND u = ?
                          """, [rate, ili_id, u])
                return True
        else:
            write_omw("""INSERT INTO ili_rating (ili_id, rating, u)
                          VALUES (?,?,?)
                      """, [ili_id, rate, u])
            return True


    def comment_ili_id(ili_id, comment, u):
        """
        This function is used to post a comment to ili ids.
        """
        ili_id = int(ili_id)
        comment = comment.strip() if comment else comment

        write_omw("""INSERT INTO ili_com (ili_id, com, u)
                           VALUES (?,?,?)
                      """, [ili_id, comment, u])
        return True


    def fetch_comment_id(ili_ids, u=None):
        """
        This function takes a list of ili ids and, optionally a username.
        It returns a dictionary with the comments filtered by the ids and,
        if provided, for that specific user.
        """
        comments = dd(list)
        ili_list = (",".join("?" for s in ili_ids), ili_ids)
        if u:
            for r in query_omw("""SELECT id, ili_id, com, u, t
                                  FROM ili_com
                                  WHERE ili_id in ({})
                                  AND   u = ?""".format(ili_list[0]),
                               ili_list[1]+[u]):
                comments[r['ili_id']].append((r['com'], r['u'], r['t']))
        else:
            for r in query_omw("""SELECT id, ili_id, com, u, t
                                  FROM ili_com
                                  WHERE ili_id in ({})
                               """.format(ili_list[0]),
                               ili_list[1]):
                comments[r['ili_id']].append((r['com'], r['u'], r['t']))

        return comments





    def fetch_ili(ili_ids=None):

        src_id = fetch_src()
        kind_id = fetch_kind()
        status_id = fetch_status()

        ili = dict()
        ili_defs = dict()
        if ili_ids:
            ili_list = (",".join("?" for s in ili_ids), ili_ids)
            for c in query_omw("""SELECT * FROM ili WHERE id in (%s)
                               """ % (ili_list[0]), ili_list[1]):
                ili[c['id']] = (kind_id[c['kind_id']], c['def'],
                                src_id[c['origin_src_id']], c['src_key'],
                                status_id[c['status_id']], c['superseded_by_id'],
                                c['t'])
                ili_defs[c['def']]=c['id']
        else:
            for c in query_omw("""SELECT * FROM ili """):
                ili[c['id']] = (kind_id[c['kind_id']], c['def'],
                                src_id[c['origin_src_id']], c['src_key'],
                                status_id[c['status_id']], c['superseded_by_id'],
                                c['t'])
                ili_defs[c['def']]=c['id']

        return ili, ili_defs

    def fetch_ili_status(status):

        src_id = fetch_src()
        kind_id = fetch_kind()
        status_id = fetch_status()

        ili = dict()
        for c in query_omw("""SELECT * FROM ili WHERE status_id = ?""", [status]):
            ili[c['id']] = (kind_id[c['kind_id']], c['def'],
                            src_id[c['origin_src_id']], c['src_key'],
                            status_id[c['status_id']], c['superseded_by_id'],
                                 c['t'])
        return ili






    def insert_new_language(bcp, iso, name, u):
        """
        This function is used to add a new language to the system.
        Only the bcp47 code and the language name are required.
        """
        if (bcp and name and u \
            and (not fetch_key_bcp_lang_code(bcp))):

            try:
                bcp = bcp.strip() if bcp else bcp
                iso = iso.strip() if iso else iso
                name = name.strip() if name else name
                lastid = write_omw("""INSERT INTO lang (bcp47, iso639, u)
                                      VALUES (?,?,?)
                                   """, [bcp, iso, u])
                write_omw("""INSERT INTO lang_name (lang_id, in_lang_id,
                                                    name, u)
                             VALUES (?,?,?,?)
                          """, [lastid, 1, name, u])

                return True
            except:
                return False

        else:
            return False




    # OMW

    def fetch_pos():
        pos_id = dd(lambda: dd())
        for r in query_omw("""SELECT id, tag, def FROM pos"""):
            pos_id['id'][r['id']]=r['tag']
            pos_id['tag'][r['tag']]=r['id']
            pos_id['def'][r['id']]=r['def']
        return pos_id

    def fetch_ssrel():
        ssrel_dict = dd(lambda: dd())
        for r in query_omw("""SELECT id, rel, def FROM ssrel"""):
            ssrel_dict['id'][r['id']]=(r['rel'],r['def'])
            ssrel_dict['rel'][r['rel']]=(r['id'],r['def'])
        return ssrel_dict

    def fetch_def_by_ssid_lang_text(ss_id, lang_id, d):
        for r in query_omw(""" SELECT id, ss_id, lang_id, def FROM def
                              WHERE ss_id = ?
                              AND lang_id = ?
                              AND def = ?""",
                          [ss_id, lang_id, d]):
            return r['id']

    def fetch_ssexe_by_ssid_lang_text(ss_id, lang_id, e):
        for r in query_omw(""" SELECT id, ss_id, lang_id, ssexe FROM ssexe
                              WHERE ss_id = ?
                              AND lang_id = ?
                              AND ssexe = ?""",
                          [ss_id, lang_id, e]):
            return r['id']


    def fetch_ss_basic(synset_list):

        synset_list = list(synset_list)
        ss_list = (",".join("?" for s in synset_list), synset_list)

        ss = dict() # ss[ss_id][s_id] = [wid, fid, lang_id, pos_id]
        for r in query_omw(""" SELECT id, ili_id, pos_id FROM ss
                WHERE id in (%s) """ % (ss_list[0]), ss_list[1]):
            ss[r['id']] = (r['ili_id'], r['pos_id'])


        senses = dd(lambda: dd(list)) # senses[ss_id][lang] = [(s_id, lemma, freq), ]
        s_tmp = list()
        s_list = list()
        for r in query_omw("""
                SELECT lang_id, lemma, w_id, canon, ss_id, s_id
                FROM ( SELECT w_id, canon, ss_id, s_id
                       FROM ( SELECT id as s_id, ss_id, w_id FROM s
                              WHERE ss_id in (%s)) as sense
                       JOIN w ON w_id = w.id ) as word
                JOIN f ON canon = f.id
                 """ % (ss_list[0]), ss_list[1]):
            s_tmp.append((r['ss_id'], r['lang_id'], r['s_id'], r['lemma']))
            s_list.append(r['s_id'])

        sfreq = dd(int)
        for r in query_omw("""SELECT s_id, sml_id as freq FROM sm 
                              WHERE s_id in (%s) and smt_id=1"""
                           % ",".join("?" for s in s_list), s_list):
            sfreq[r['s_id']] = r['freq']

        for (ss_id, lang_id, s_id, lemma) in s_tmp:  
            senses[ss_id][lang_id].append((s_id, lemma, sfreq[s_id]))
        for ss_id in senses:
            for lang_id in senses[ss_id]:
                senses[ss_id][lang_id].sort(key=lambda x: x[2], reverse=True)

        defs = dd(lambda: dd(list)) # defs[ss_id][lang] = [def, def2]
        for r in query_omw(""" SELECT ss_id, lang_id, def FROM def
                WHERE ss_id in (%s) """ % (ss_list[0]), ss_list[1]):
            defs[r['ss_id']][r['lang_id']].append(r['def'])


        exes = dd(lambda: dd(list)) # exs[ss_id][lang] = [ex, ex2]
        for r in query_omw(""" SELECT ss_id, lang_id, ssexe FROM ssexe
                WHERE ss_id in (%s) """ % (ss_list[0]), ss_list[1]):
            exes[r['ss_id']][r['lang_id']].append(r['ssexe'])


        links = dd(lambda: dd(list)) # links[ss1_id][ssre] = [ss2_id, ...]
        for r in query_omw(""" SELECT ss1_id, ssrel_id, ss2_id FROM sslink
                WHERE ss1_id in (%s) """ % (ss_list[0]), ss_list[1]):
            links[r['ss1_id']][r['ssrel_id']].append(r['ss2_id'])

            
        return ss, senses, defs, exes, links

    def fetch_sense(s_id):
        """return information about the sense
           FIXME:
        """
        # sense = (lemma, pos, freq, w_id, ss_id, ili_id)
        sense=[]
        for r in query_omw("""
                SELECT  lemma, w_id, canon, ss_id, pos_id, ili_id
                FROM ( SELECT lemma, w_id, canon, ss_id
                    FROM ( SELECT w_id, canon, ss_id
                        FROM ( SELECT ss_id, w_id FROM s
                             WHERE id=? ) as sense
                        JOIN w ON w_id = w.id ) as word
                     JOIN f ON canon = f.id ) as thing
                 JOIN ss on ss.id=ss_id
                 """, (s_id,)):
            sense = [r['lemma'], r['pos_id'], 0,
                     r['w_id'],  r['ss_id'], r['ili_id']]
        ### NOTE hard-coding frequency type smt_id=1
        for r in query_omw("""SELECT sml_id as freq FROM sm 
                              WHERE s_id=? and smt_id=1""", (s_id,)):
            if r['freq']:
                sense[2] =  r['freq']

        return sense


    def fetch_labels(lang_id, sss):
        """return a dict with lang_id labels for the synsets in sss"""
        labels = dict()
        for r in query_omw("""SELECT ss_id, label FROM label 
        WHERE lang_id = ? AND ss_id in (%s)""" % ",".join('?' for s in sss),
                           [lang_id] + list(sss)):
            labels[r['ss_id']]=r['label']
        return labels
        
    
    def fetch_ss_id_by_src_orginalkey(src_id, originalkey):
        for r in query_omw(""" SELECT ss_id, src_id, src_key FROM ss_src
                WHERE src_id = ? and src_key = ? """, [src_id, originalkey]):
            ss = r['ss_id']
        return ss

    def fetch_all_defs_by_ss_lang_text():
        defs = dd(lambda: dd())
        for r in query_omw("""SELECT id, ss_id, lang_id, def FROM def"""):
            defs[r['ss_id']][(r['lang_id'],r['def'])]=r['id']
        return defs

    def fetch_all_ssexe_by_ss_lang_text():
        ssexes = dd(lambda: dd())
        for r in query_omw("""SELECT id, ss_id, lang_id, ssexe FROM ssexe"""):
            ssexes[r['ss_id']][(r['lang_id'],r['ssexe'])]=r['id']
        return ssexes

    def fetch_all_ssrels_by_ss_rel_trgt():
        sslinks = dd(lambda: dd())
        for r in query_omw("""SELECT id, ss1_id, ssrel_id, ss2_id
                              FROM sslink"""):
            sslinks[r['ss1_id']][(r['ssrel_id'],r['ss2_id'])]=r['id']
        return sslinks

    def fetch_all_forms_by_lang_pos_lemma():
        forms = dd(lambda: dd())
        for r in query_omw("""SELECT id, lang_id, pos_id, lemma
                              FROM f"""):
            forms[r['lang_id']][(r['pos_id'],r['lemma'])]=r['id']
        return forms

    def f_ss_id_by_ili_id(ili_id):
        """ Return a list of ss_ids from an ili_id """
        ss_ids = list()
        for r in query_omw("""SELECT id FROM ss
                              WHERE ili_id = ?""", [ili_id]):
            ss_ids.append(r['id'])
        return ss_ids


    def f_ili_ss_id_map():
        """ Returns a dictionary linking ili_ids and ss_ids. It is possible
            that one ili_id links to multiple ss_ids, but one ss_id can only
            link to a single ili_id. """
        ili_ss_map = dd(lambda: dd(list))
        for r in query_omw("""SELECT id, ili_id, pos_id FROM ss"""):
            ili_ss_map['ili'][r['ili_id']].append((r['id'],r['pos_id']))
            ili_ss_map['ss'][r['id']] = r['ili_id']

        return ili_ss_map



    def f_sslink_id_by_ss1_rel_ss2(ss1, rel, ss2):
        "Return sslink_id, if any, from sslink."

        for r in query_omw("""SELECT id
                              FROM sslink
                              WHERE ss1_id = ?
                              AND ssrel_id = ?
                              AND ss2_id = ?""",
                           [ss1, rel, ss2]):
            return r['id']


    def insert_omw_ss(ili_id, pos_id, u):
        return write_omw("""INSERT INTO ss (ili_id, pos_id, u)
                            VALUES (?,?,?)""",
                         [ili_id, pos_id, u])

    def blk_insert_omw_ss(tuple_list):
        """ tuple_list = [(id, ili_id, pos_id, u), ...]"""
        return blk_write_omw("""INSERT INTO ss (id, ili_id, pos_id, u)
                                VALUES (?,?,?,?)""", tuple_list)


    def insert_omw_ss_src(ss_id, src_id, src_key, conf, u):
        return write_omw("""INSERT INTO ss_src (ss_id, src_id, src_key, conf, u)
                            VALUES (?,?,?,?,?)""",
                         [ss_id, src_id, src_key, conf, u])

    def blk_insert_omw_ss_src(tuple_list):
        return blk_write_omw("""INSERT INTO ss_src (ss_id, src_id, src_key, conf, u)
                                VALUES (?,?,?,?,?)""", tuple_list)


    def insert_omw_def(ss_id, lang_id, d, u):
        return write_omw("""INSERT INTO def (ss_id, lang_id, def, u)
                            VALUES (?,?,?,?)""",
                         [ss_id, lang_id, d, u])

    def blk_insert_omw_def(tuple_list):
        return blk_write_omw("""INSERT INTO def (id, ss_id, lang_id, def, u)
                                VALUES (?, ?,?,?,?)""", tuple_list)

    def insert_omw_def_src(def_id, src_id, conf, u):
        return write_omw("""INSERT INTO def_src (def_id, src_id, conf, u)
                            VALUES (?,?,?,?)""",
                         [def_id, src_id, conf, u])

    def blk_insert_omw_def_src(tuple_list):
        return blk_write_omw("""INSERT INTO def_src (def_id, src_id, conf, u)
                                VALUES (?,?,?,?)""", tuple_list)

    def insert_omw_ssexe(ss_id, lang_id, e, u):
        return write_omw("""INSERT INTO ssexe (ss_id, lang_id, ssexe, u)
                            VALUES (?,?,?,?)""",
                         [ss_id, lang_id, e, u])

    def blk_insert_omw_ssexe(tuple_list):
        return blk_write_omw("""INSERT INTO ssexe (id, ss_id, lang_id, ssexe, u)
                                VALUES (?,?,?,?,?)""", tuple_list)


    def insert_omw_ssexe_src(ssexe_id, src_id, conf, u):
        return write_omw("""INSERT INTO ssexe_src (ssexe_id, src_id, conf, u)
                            VALUES (?,?,?,?)""",
                         [ssexe_id, src_id, conf, u])

    def blk_insert_omw_ssexe_src(tuple_list):
        return blk_write_omw("""INSERT INTO ssexe_src (ssexe_id, src_id, conf, u)
                                VALUES (?,?,?,?)""", tuple_list)

    def insert_omw_sslink(ss1_id, ssrel_id, ss2_id, u):
        return write_omw("""INSERT INTO sslink (ss1_id, ssrel_id, ss2_id, u)
                            VALUES (?,?,?,?)""",
                         [ss1_id, ssrel_id, ss2_id, u])

    def blk_insert_omw_sslink(tuple_list):
        return blk_write_omw("""INSERT INTO sslink (id, ss1_id, ssrel_id, ss2_id, u)
                                VALUES (?,?,?,?,?)""", tuple_list)

    def insert_omw_sslink_src(sslink_id, src_id, conf, lang_id, u):
        return write_omw("""INSERT INTO sslink_src (sslink_id, src_id, conf, lang_id, u)
                            VALUES (?,?,?,?,?)""",
                         [sslink_id, src_id, conf, lang_id, u])

    def blk_insert_omw_sslink_src(tuple_list):
        return blk_write_omw("""INSERT INTO sslink_src (sslink_id, src_id, conf, lang_id, u)
                                VALUES (?,?,?,?,?)""", tuple_list)


    # FORM
    def insert_omw_f(lang_id, pos_id, form, u):
        return write_omw("""INSERT INTO f (lang_id, pos_id, lemma, u)
                            VALUES (?,?,?,?)""",
                         [lang_id, pos_id, form, u])

    # BLK FORM
    def blk_insert_omw_f(tuple_list):
        return blk_write_omw("""INSERT INTO f (id, lang_id, pos_id, lemma, u)
                                VALUES (?,?,?,?,?)""", tuple_list)

    # FORM SRC
    def insert_omw_f_src(f_id, src_id, conf, u):
        return write_omw("""INSERT INTO  f_src (f_id, src_id, conf, u)
                            VALUES (?,?,?,?)""",
                         [f_id, src_id, conf, u])

    # BLK FORM SRC
    def blk_insert_omw_f_src(tuple_list):
        return blk_write_omw("""INSERT INTO f_src (f_id, src_id, conf, u)
                                VALUES (?,?,?,?)""", tuple_list)

    # WORD
    def insert_omw_w(canon, u):
        return write_omw("""INSERT INTO w (canon, u)
                            VALUES (?,?)""",
                         [canon, u])

    # BLK WORD
    def blk_insert_omw_w(tuple_list):
        return blk_write_omw("""INSERT INTO w (id, canon, u)
                                VALUES (?,?,?)""", tuple_list)

    # WORD-FORM LINK
    def insert_omw_wf_link(w_id, f_id, src_id, conf, u):
        return write_omw("""INSERT INTO wf_link (w_id, f_id, src_id, conf, u)
                            VALUES (?,?,?,?,?)""",
                         [w_id, f_id, src_id, conf, u])

    # BLK WORD-FORM LINK
    def blk_insert_omw_wf_link(tuple_list):
        return blk_write_omw("""INSERT INTO  wf_link (w_id, f_id, src_id, conf, u)
                            VALUES (?,?,?,?,?)""", tuple_list)

    # SENSE
    def insert_omw_s(ss_id, w_id, u):
        return write_omw("""INSERT INTO s (ss_id, w_id, u)
                            VALUES (?,?,?)""",
                         [ss_id, w_id, u])

    # BLK SENSE
    def blk_insert_omw_s(tuple_list):
        return blk_write_omw("""INSERT INTO s (id, ss_id, w_id, u)
                                VALUES (?,?,?,?)""", tuple_list)

    # SENSE SRC
    def insert_omw_s_src(s_id, src_id, conf, u):
        return write_omw("""INSERT INTO s_src (s_id, src_id, conf, u)
                            VALUES (?,?,?,?)""",
                         [s_id, src_id, conf, u])

    # BLK SENSE SRC
    def blk_insert_omw_s_src(tuple_list):
        return blk_write_omw("""INSERT INTO s_src (s_id, src_id, conf, u)
                                VALUES (?,?,?,?)""", tuple_list)
