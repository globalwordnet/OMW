#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict as dd

from omw.common_sql import (
    qs,
    connect_omw,
    connect_admin,
    query_omw,
    query_omw_direct,
    write_omw,
    blk_write_omw
)

from omw import app
#ntsense=namedtuple('Sense', ['lemma', 'y'], verbose=True)
import gwadoc

with app.app_context():

    def init_omw_db():
        omw = connect_omw()
        with app.open_resource('schemas/omw.sql') as f:
            omw.executescript(f.read().decode('utf-8'))

    def init_admin_db():
        admin = connect_admin()
        with app.open_resource('schemas/admin.sql') as f:
            admin.executescript(f.read().decode('utf-8'))

    def l2q (l):
        """return a comma seperated list of question marks
        useful for sql queries over lists"""
        return ",".join('?' for e in l)

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
        """
        Return a mapping of {src.id: (proj.code, src.version)}

        Example:
        >>> next(fetch_src())
        {1: ('pwn', '3.0')}

        """
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
        # print(proj,version)
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

    
    def fetch_src_id_pos_stats(src_id):
        src_pos_stats=dd(lambda: dd(int))
        pos = fetch_pos()
        r  =  query_omw_direct("""    
        SELECT pos_id, count(distinct s.ss_id),
        count(distinct s.w_id), count(distinct s.id)
        FROM s JOIN s_src
        ON s.id=s_src.s_id
        JOIN ss ON s.ss_id=ss.id
        WHERE s_src.src_id=? group by pos_id""", (src_id,))
        for (p, ss, w, s) in r:
            ps =  pos['id'][p] 
            src_pos_stats[ps]['synsets'] = ss
            src_pos_stats[ps]['words'] = w
            src_pos_stats[ps]['senses'] = s
        return  src_pos_stats

    def fetch_ssrel_stats(src_id):
        """ Return the number of links for each type for sense-sense links
            for a wordnet with the given src_id
        """
        constitutive = ['instance_hyponym','instance_hypernym',
                         'hypernym', 'hyponym',
                         'synonym', 'antonym',
                         'mero_part', 'holo_part',
                         'mero_member', 'holo_member',
                         'mero_substance', 'holo_substance' ]
        src_ssrel_stats = dd(int)
        ssrl=fetch_ssrel()
        for r in query_omw("""
        SELECT  ssrel_id, count(ssrel_id)
        FROM sslink JOIN sslink_src
        ON sslink.id=sslink_src.sslink_id
        WHERE sslink_src.src_id=?
        GROUP BY ssrel_id""", [src_id]):
            link = ssrl['id'][r['ssrel_id']]
            src_ssrel_stats[link[0]] = r['count(ssrel_id)']
            src_ssrel_stats['TOTAL'] += r['count(ssrel_id)']
            if link[0] in constitutive:
                src_ssrel_stats['CONSTITUTIVE'] += r['count(ssrel_id)']
            
        return src_ssrel_stats

    def fetch_srel_stats(src_id):
        """ Return the number of links for each type for sense-sense links
            for a wordnet with the given src_id
        """
        src_srel_stats = dd(int)
        srl=fetch_srel()
        for r in query_omw("""
        SELECT  srel_id, count(srel_id)
        FROM slink JOIN slink_src
        ON slink.id=slink_src.slink_id
        WHERE slink_src.src_id=?
        GROUP BY srel_id""", [src_id]):
            link = srl['id'][r['srel_id']]
            src_srel_stats[link[0]] = r['count(srel_id)']
            src_srel_stats['TOTAL'] += r['count(srel_id)']
        return src_srel_stats

    
            
    def fetch_src_id_stats(src_id):
        src_id_stats=dd(int)
        
        for r in query_omw("""
        SELECT count(distinct s.ss_id), count(distinct s.id)
        FROM s JOIN s_src 
        ON s.id=s_src.s_id
        WHERE s_src.src_id=?""", [src_id]):
            src_id_stats['synsets'] = r['count(distinct s.ss_id)']
            src_id_stats['senses'] = r['count(distinct s.id)']

        for r in query_omw("""
        SELECT count(distinct w_id), count(distinct f_id)  
        FROM wf_link WHERE src_id=?""", [src_id]):
            src_id_stats['forms'] = r['count(distinct f_id)']
            src_id_stats['words'] = r['count(distinct w_id)']

        cid = query_omw('select id from resource where code = ?', ('core',), one=True)
        if cid:
            core_id = cid['id']
            for r in query_omw("""select count(distinct ss.id) 
            FROM ss JOIN ss_src ON ss.id=ss_src.ss_id JOIN ssxl ON ssxl.ss_id=ss.id 
            WHERE ss_src.src_id = ? AND ssxl.resource_id = ?""", [src_id, core_id]): 
                src_id_stats['core'] = r['count(distinct ss.id)']

        ## synsets that are used in a sense and linked to an ili                    
        for r in query_omw("""
        SELECT count(distinct id)
        FROM ss
        WHERE ss.ili_id is not NULL
        AND id IN
         (SELECT s.ss_id FROM s
          WHERE s.id IN
           (SELECT s_id FROM s_src
	        WHERE s_src.src_id=?))""", [src_id]): 
            src_id_stats['in_ili'] = r['count(distinct id)']                 

        ### Definitions
        for r in query_omw("""
        SELECT count(distinct ss_id)
        FROM def WHERE id IN
          (SELECT def_id FROM def_src
           WHERE src_id =?)""", [src_id]): 
            src_id_stats['def'] = r['count(distinct ss_id)']

        ### Examples
        for r in query_omw("""
        SELECT count(distinct ss_id)
        FROM ssexe WHERE id in 
          (SELECT ssexe_id FROM ssexe_src
           WHERE src_id =?)""", [src_id]): 
            src_id_stats['ssexe'] = r['count(distinct ss_id)']

        ### Frequency
        for r in query_omw("""
        SELECT COALESCE(sum(sml_id),0) as sum, count(sml_id) FROM sm
        WHERE smt_id = 1 AND sm.s_id IN
        (SELECT s_id FROM s_src
           WHERE src_id =?)""", [src_id]):
            src_id_stats['freq_token'] = r['count(sml_id)']
            src_id_stats['freq_type'] = r['sum']
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
    
    def fetch_src_for_ss_id(s_ids):
        """return a dict of lists of (src_ids, conf)  per synset id
           src_id[ss_id] = [(src_id, src_key, conf), ... ]
        """
        src_ssid = dd(list)
        for r in query_omw("""SELECT ss_id, src_key, src_id, conf 
        FROM ss_src WHERE ss_id in (%s)""" % qs(s_ids), s_ids):
            src_ssid[r['ss_id']].append((r['src_id'], r['src_key'], r['conf']))
        return src_ssid

         
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

    def fetch_max_slink_id():
        for r in query_omw("""SELECT MAX(id) FROM slink"""):
            return r['MAX(id)']

    def fetch_max_ssslink_id():
        for r in query_omw("""SELECT MAX(id) FROM ssslink"""):
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

    def fetch_max_sm_id():
        for r in query_omw("""SELECT MAX(id) FROM sm"""):
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
        """look up the relation and definition for synset level links
           index by an 'id' or from a 'ssrel'
           ssrel['id'][1] = ('agent', 'the undertaker of an action') 
           ssrel['rel']['agent'] = (1, 'the undertaker of an action') """
        ssrel_dict = dd(lambda: dd())
        for r in query_omw("""SELECT id, rel, def FROM ssrel"""):
            ssrel_dict['id'][r['id']]=(r['rel'],r['def'])
            ssrel_dict['rel'][r['rel']]=(r['id'],r['def'])
        return ssrel_dict

    def fetch_sssrel():
        """look up the relation and definition for sense-synset level links
           index by an 'id' or from a 'ssrel'
           ssrel['id'][1] = ('agent', 'the undertaker of an action') 
           ssrel['rel']['agent'] = (1, 'the undertaker of an action')
           FIXME link to GWADOC """
        sssrel_dict = dd(lambda: dd())
        for r in query_omw("""SELECT id, rel, def FROM ssrel"""):
            ssrel_dict['id'][r['id']]=(r['rel'],r['def'])
            ssrel_dict['rel'][r['rel']]=(r['id'],r['def'])
        return ssrel_dict
    
    def fetch_srel():
        """look up the relation and definition for sense level links
           index by an 'id' or from a 'srel'
           ssrel['id'][1] = ('antonym', 'a sense with the opposite meaning') 
           ssrel['rel']['agent'] = (1, 'a sense with the opposite meaning') """
        srel_dict = dd(lambda: dd())
        for r in query_omw("""SELECT id, rel, def FROM srel"""):
            srel_dict['id'][r['id']]=(r['rel'],r['def'])
            srel_dict['rel'][r['rel']]=(r['id'],r['def'])
        return srel_dict

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

    def fetch_s_freq(sense_list):
        """get the total frequency of each sense

        frequency is in sm:
        (s_id, smt_id, sml_id) 
           smt_id=1 (hard coded)
           sml_id is the frequency
        the source of the frequency should be in sm_src
        senses can have multiple rows of frequency 

        :returns: a dd with key sense id and value frequency
        :rtype: defaultdict(int)

        sfreq[s_id] = freq
        """
        
        sfreq = dd(int) # defaults to zero
        for r in query_omw("""SELECT s_id, SUM(sml_id) as freq FROM sm 
                              WHERE s_id in (%s) and smt_id=1
                              GROUP BY s_id"""
                           % l2q(sense_list), sense_list):
            sfreq[r['s_id']] = r['freq']
        return sfreq
            
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

        sfreq = fetch_s_freq(s_list)

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


        links = dd(lambda: dd(list)) # links[ss1_id][ssrel] = [ss2_id, ...]
        for r in query_omw(""" SELECT ss1_id, ssrel_id, ss2_id FROM sslink
                WHERE ss1_id in (%s) """ % (ss_list[0]), ss_list[1]):
            links[r['ss1_id']][r['ssrel_id']].append(r['ss2_id'])

            
        return ss, senses, defs, exes, links

    def fetch_core():
        """return sets of core synsets as OMW synsets and ILIs"""
        core_ss = set()
        core_ili = set()
        r = query_omw('select id from resource where code = ?', ('core',), one=True)
        # print(r)
        if r:
            rid = r['id']
            for q in  query_omw("""SELECT ss_id, x1 FROM ssxl WHERE resource_id=?""", (rid,)):
                core_ss.add(q['ss_id'])
                core_ili.add(q['x1'])
        return core_ss, core_ili

    def fetch_cili_tsv():
        """output the ili as tsv, with lists of linked synsets

        the data is accessible at "/cili.tsv"  
        and documented on the CILI welcome page
        """
        ### get projects linked to ili        
        srcs = fetch_src()
        src = dd(list)
        r = query_omw_direct("SELECT ss_id, src_id, src_key from ss_src")
        for (ss_id, src_id, src_key) in r:
            src[ss_id].append("{}-{}:{}".format(srcs[src_id][0],
                                                srcs[src_id][1],
                                                src_key))
        ### prepare headers
        tsv=["\t".join(["ili_id",
                       "status",
                       "superseded_by",
                       "origin",
                       "used_by",
                       "definition"])]

        ### get the data
        r  =  query_omw_direct("""SELECT ss.id, ili.id,  def, 
     status_id,  superseded_by_id, origin_src_id, src_key
        FROM  ili LEFT JOIN ss on ss.ili_id = ili.id""")
        for (ss_id, ili_id, dfn, status_id,
             superseded_by_id, origin_src_id, src_key) in r:
            tsv.append("\t".join(['i' + str(ili_id),
                                  str(status_id),
                                  'i' + str(superseded_by_id) if superseded_by_id else '',
                                  "{}-{}:{}".format(srcs[origin_src_id][0],
                                                    srcs[ origin_src_id][1],
                                                    src_key),
                                  ";".join(src[ss_id]),
                                  dfn]))
        return "\n".join(tsv)+"\n"
    
    def fetch_sense_links(s_ids):
        """ return information about the links to a list of senses
        slinks[s_id_from][srel] = [s_id_to, ...]
        """
        slinks = dd(lambda: dd(list))  # links[srel] = [s2_id, ...]
        for r in query_omw(""" SELECT s1_id, srel_id, s2_id FROM slink
                WHERE s1_id in ({})""".format(l2q(s_ids)), s_ids):
            slinks[r['s1_id']][r['srel_id']].append(r['s2_id'])
        return slinks
        
    
    def fetch_sense(s_id):
        """ return information about the sense
          
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
        ### NOTE may want to show the different sources of frequencies
        sfreq = fetch_s_freq([s_id])
        sense[2] = sfreq[s_id]

        return sense

    def fetch_forms(w_id):
        """return the forms of all variants
        FIXME: should include meta data
        """
        # variant = [lemma]
        forms=[]
        for r in query_omw("""
        SELECT lemma, id as f_id
        FROM (SELECT f_id FROM wf_link
	      WHERE w_id = ?)
        JOIN f on f.id=f_id""", (w_id,)):
            forms.append(r['lemma'])
        return forms

    def fetch_labels(lang_id, sss):
        """return a dict with lang_id labels for the synsets in sss"""
        labels = dict()
        for r in query_omw("""SELECT ss_id, label FROM label 
        WHERE lang_id = ? AND ss_id in (%s)""" % l2q(sss),
                           [lang_id] + list(sss)):
            labels[r['ss_id']]=r['label']
        return labels

    def fetch_sense_labels(s_ids):
        """return just the string for the canonical form for each of a list of sense ids
        slabel[s_id] = lemma (s_id is the id of the sense)
        slabel[127262] = 'driver' """
        slabel = dict()
        for r in query_omw("""SELECT lemma, s_id, canon
        FROM ( SELECT w_id, canon, s_id
           FROM ( SELECT id as s_id, w_id FROM s
              WHERE id in ({}) ) as sense
           JOIN w ON w_id = w.id ) as word
        JOIN f ON canon = f.id""".format(l2q(s_ids)),
                           s_ids):
            slabel[r['s_id']] = r['lemma']
        return slabel
        
    
    def fetch_ss_id_by_src_orginalkey(src_id, originalkey):
        for r in query_omw(""" SELECT ss_id, src_id, src_key FROM ss_src
                WHERE src_id = ? and src_key = ? """, [src_id, originalkey]):
            ss = r['ss_id']
        return ss

    def fetch_defs_by_sense(s_ids):
        """given a list of senses, return a dictionary of definitions"""
        ### FIXME: find the sense level definition when defined
        defs=dd(lambda: dict())
        for r in query_omw(""" SELECT s_id, lang_id, def 
        FROM (SELECT id AS s_id, ss_id FROM s 
        WHERE id IN ({})) as sense
        JOIN def ON sense.ss_id = def.ss_id""".format(l2q(s_ids)), s_ids):
            defs[r['s_id']][r['lang_id']] = r['def']
        return defs

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

    def fetch_all_srels_by_s_rel_trgt():
        slinks = dd(lambda: dd())
        for r in query_omw("""SELECT id, s1_id, srel_id, s2_id
                              FROM slink"""):
            slinks[r['s1_id']][(r['srel_id'],r['s2_id'])]=r['id']
        return slinks

    def fetch_all_sssrels_by_s_rel_trgt():
        ssslinks = dd(lambda: dd())
        for r in query_omw("""SELECT id, s_id, srel_id, ss_id
                              FROM ssslink"""):
            ssslinks[r['s_id']][(r['srel_id'],r['ss_id'])]=r['id']
        return ssslinks

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
        """
        insert a list of (id, ss1_id, ssrel_id, ss2_id, u) into sslink
        often followed by insert_omw_sslink_src()
        if id is NULL, it will autoincrement
        """
        return blk_write_omw("""INSERT INTO sslink (id, ss1_id, ssrel_id, ss2_id, u)
                                VALUES (?,?,?,?,?)""", tuple_list)

    def insert_omw_sslink_src(sslink_id, src_id, conf, lang_id, u):
        return write_omw("""INSERT INTO sslink_src (sslink_id, src_id, conf, lang_id, u)
                            VALUES (?,?,?,?,?)""",
                         [sslink_id, src_id, conf, lang_id, u])

    def blk_insert_omw_sslink_src(tuple_list):
        return blk_write_omw("""INSERT INTO sslink_src (sslink_id, src_id, conf, lang_id, u)
                                VALUES (?,?,?,?,?)""", tuple_list)

    def insert_omw_slink(s1_id, srel_id, s2_id, u):
        return write_omw("""INSERT INTO slink (s1_id, srel_id, s2_id, u)
                            VALUES (?,?,?,?)""",
                         [s1_id, srel_id, s2_id, u])

    def blk_insert_omw_slink(tuple_list):
        return blk_write_omw("""INSERT INTO slink (id, s1_id, srel_id, s2_id, u)
                                VALUES (?,?,?,?,?)""", tuple_list)

    def insert_omw_slink_src(slink_id, src_id, conf, u):
        return write_omw("""INSERT INTO slink_src (slink_id, src_id, conf, u)
                            VALUES (?,?,?,?)""",
                         [slink_id, src_id, conf, u])

    def blk_insert_omw_slink_src(tuple_list):
        return blk_write_omw("""INSERT INTO slink_src (slink_id, src_id, conf, u)
                                VALUES (?,?,?,?)""", tuple_list)

    def insert_omw_ssslink(s_id, srel_id, ss_id, u):
        return write_omw("""INSERT INTO ssslink (s_id, srel_id, ss_id, u)
                            VALUES (?,?,?,?)""",
                         [s_id, srel_id, ss_id, u])

    def blk_insert_omw_ssslink(tuple_list):
        return blk_write_omw("""INSERT INTO ssslink (id, s_id, srel_id, ss_id, u)
                                VALUES (?,?,?,?,?)""", tuple_list)

    def insert_omw_ssslink_src(ssslink_id, src_id, conf, lang_id, u):
        return write_omw("""INSERT INTO ssslink_src (ssslink_id, src_id, conf, lang_id, u)
                            VALUES (?,?,?,?,?)""",
                         [ssslink_id, src_id, conf, lang_id, u])

    def blk_insert_omw_ssslink_src(tuple_list):
        return blk_write_omw("""INSERT INTO ssslink_src (ssslink_id, src_id, conf, lang_id, u)
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


    # INSERT SENSE META
    def insert_omw_sm(s_id, smt_id, sml_id, u):
        """
        smt_id = sense-meta-tag_id (db restricted to the ones stored in smt)
        sml_id = labels (not restricted, but meanings available in sml)
        """
        return write_omw("""INSERT INTO sm (s_id, smt_id, sml_id, u)
                            VALUES (?,?,?,?)""",
                         [s_id, smt_id, sml_id, u])

    # BLK INSERT SENSE META
    def blk_insert_omw_sm(tuple_list):
        return blk_write_omw("""INSERT INTO sm (id, s_id, smt_id, sml_id, u)
                                VALUES (?,?,?,?,?)""", tuple_list)

    # INSERT SENSE META SRC
    def insert_omw_sm_src(sm_id, src_id, conf, u):
        return write_omw("""INSERT INTO sm_src (sm_id, src_id, conf, u)
                            VALUES (?,?,?,?)""",
                         [sm_id, src_id, conf, u])

    # BLK SENSE META SRC
    def blk_insert_omw_sm_src(tuple_list):
        return blk_write_omw("""INSERT INTO sm_src (sm_id, src_id, conf, u)
                                VALUES (?,?,?,?)""", tuple_list)

    def fetch_graph():
        """
        get the complete hypernym graph (including instances)
        if the node is in ili, its name is iXXXX
        else the node is oXXXX

        return a dictionary of sets
          graph[hype] = {hypo, hypo, hypo, ...}
        """
        graph = dd(set)
        for r in query_omw("""SELECT ss1_id, ssrel_id, ss2_id 
                    FROM sslink
                    WHERE ssrel_id in (34,37, 35, 38)"""):
            if r['ssrel_id'] in [34,37]: # hype, ihype
                graph[r['ss2_id']].add(r['ss1_id'])
            else:
                graph[r['ss1_id']].add(r['ss2_id'])
        return graph

    # UPDATE LABELS
    def updateLabels():
        """This functions is to be run after a new wordnet is uploaded
        so that concept labels for that language are created and visible
        as concept names.
        """
        sfreq = fetch_s_freq(s_list)

        senses =dd(lambda: dd(list))
        #senses[ss_id][lang_id]=[(ls_id, lemma, freq), ...]
        forms = dd(lambda: dd(int))
        #forms[lang][word] = freq
        eng_id=1 ### we know this :-)


        for r in query_omw("""SELECT s_id, ss_id, lemma, lang_id
                              FROM (SELECT w_id, canon, ss_id, s_id
                              FROM (SELECT id as s_id, ss_id, w_id FROM s)
                              JOIN w ON w_id = w.id )
                              JOIN f ON canon = f.id"""):


            senses[r['ss_id']][r['lang_id']].append((r['s_id'], r['lemma'], sfreq[r['s_id']]))
            forms[r['lang_id']][r['lemma']] += 1

        # make the best label for each language that has lemmas    
        for ss in senses:
            for l in senses[ss]:
                senses[ss][l].sort(key=lambda x: (-x[2],  ### sense freq (freq is good)
                                          forms[l][x[1]], ### uniqueness (freq is bad)
                                          len(x[1]),  ### length (short is good)
                                          x[1]))      ### lemma (so it is the same)
        
        lgs=[]
        cv = query_omw_direct("SELECT id FROM lang ORDER BY id") ### English first!
        for (lid,) in cv:
            lgs.append(lid)       

        # make the labels
        label = dd(lambda: dd(str))
        values=list()

        for ss in senses:
            for l in lgs:
                if senses[ss][l]:
                    label[ss][l]=senses[ss][l][0][1]
                else:
                    for lx in lgs:  ### start with eng and go through till you find one
                        if senses[ss][lx]:
                            label[ss][l]=senses[ss][lx][0][1]
                            break
                    else:
                        label[ss][l]="?????"
                values.append((ss, l,  label[ss][l]))


        # write the labels (delete old ones first)
        write_omw("""DELETE FROM label""")
        blk_write_omw("""INSERT INTO label(ss_id, lang_id, label, u)
                         VALUES (?,?,?,"omw")""", values)

        return True
