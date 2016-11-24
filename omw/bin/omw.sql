/* Active User (used to record who deleted what) */

CREATE TABLE active_user
       (id INTEGER PRIMARY KEY ASC,
       user_id TEXT NOT NULL);



CREATE TABLE lang
       (id INTEGER PRIMARY KEY ASC,
        bcp47 TEXT NOT NULL,
        iso639 TEXT,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

CREATE UNIQUE INDEX lang_bcp47_index ON lang (bcp47);

CREATE TABLE lang_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        id_old INTEGER, id_new INTEGER,
        bcp47_old TEXT, bcp47_new TEXT,
        iso639_old TEXT, iso639_new TEXT,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);

CREATE TRIGGER lang_insert AFTER INSERT ON lang
       BEGIN
       INSERT INTO lang_log  (action,
                              id_new,
                              bcp47_new,
                              iso639_new,
                              u_new,
                              t_new)

       VALUES ('INSERT',
                new.id,
                new.bcp47,
                new.iso639,
                new.u,
                new.t);

       END;


CREATE TRIGGER lang_update AFTER UPDATE ON lang
       BEGIN
       INSERT INTO lang_log  (action,
                              id_old, id_new,
                              bcp47_old, bcp47_new,
                              iso639_old, iso639_new,
                              u_old, u_new,
                              t_old, t_new)

       VALUES ('UPDATE',
                old.id, new.id,
                old.bcp47, new.bcp47,
                old.iso639, new.iso639,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER lang_delete AFTER DELETE ON lang
       BEGIN
       INSERT INTO lang_log  (action,
                              id_old,
                              bcp47_old,
                              iso639_old,
                              u_old, u_new,
                              t_old, t_new)

       VALUES ('DELETE',
                old.id,
                old.bcp47,
                old.iso639,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);

       END;


CREATE TABLE lang_name
       (lang_id INTEGER NOT NULL,
        in_lang_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (lang_id, in_lang_id),
        FOREIGN KEY(lang_id) REFERENCES lang(id),
        FOREIGN KEY(in_lang_id) REFERENCES lang(id));

CREATE UNIQUE INDEX lang_id_index ON lang_name (lang_id, in_lang_id);


CREATE TABLE lang_name_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        lang_id_old INTEGER, lang_id_new INTEGER,
        in_lang_id_old INTEGER, in_lang_id_new INTEGER,
        name_old TEXT, name_new TEXT,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER lang_name_insert AFTER INSERT ON lang_name
       BEGIN
       INSERT INTO lang_name_log  (action,
                                   lang_id_new,
                                   in_lang_id_new,
                                   name_new,
                                   u_new,
                                   t_new)

       VALUES ('INSERT',
               new.lang_id,
               new.in_lang_id,
               new.name,
               new.u,
               new.t);
       END;


CREATE TRIGGER lang_name_update AFTER UPDATE ON lang_name
       BEGIN
       INSERT INTO lang_name_log  (action,
                                   lang_id_old, lang_id_new,
                                   in_lang_id_old, in_lang_id_new,
                                   name_old, name_new,
                                   u_old, u_new,
                                   t_old, t_new)

       VALUES ('UPDATE',
                old.lang_id, new.lang_id,
                old.in_lang_id, new.in_lang_id,
                old.name, new.name,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER lang_name_delete AFTER DELETE ON lang_name
       BEGIN
       INSERT INTO lang_name_log  (action,
                                   lang_id_old,
                                   in_lang_id_old,
                                   name_old,
                                   u_old, u_new,
                                   t_old, t_new)

       VALUES ('DELETE',
                old.lang_id,
                old.in_lang_id,
                old.name,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;




/* Kind (Concept Kinds) */

CREATE TABLE kind
       (id INTEGER PRIMARY KEY ASC,
        kind TEXT NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE kind_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        id_old INTEGER, id_new INTEGER,
        kind_old TEXT, kind_new TEXT,
        u_old INTEGER, u_new INTEGER NOT NULL,
        t_old TIMESTAMP, t_new TIMESTAMP);

CREATE TRIGGER kind_insert AFTER INSERT ON kind
       BEGIN
       INSERT INTO kind_log  (action,
                              id_new,
                              kind_new,
                              u_new,
                              t_new)

       VALUES ('INSERT',
               new.id,
               new.kind,
               new.u,
               new.t);
       END;

CREATE TRIGGER kind_update AFTER UPDATE ON kind
       BEGIN
       INSERT INTO kind_log  (action,
                              id_old, id_new,
                              kind_old, kind_new,
                              u_old, u_new,
                              t_old, t_new)

       VALUES ('UPDATE',
                old.id, new.id,
                old.kind, new.kind,
                old.u, new.u,
                old.t, new.t);
       END;

CREATE TRIGGER kind_delete AFTER DELETE ON kind
       BEGIN
       INSERT INTO kind_log  (action,
                              id_old,
                              kind_old,
                              u_old, u_new,
                              t_old, t_new)

       VALUES ('DELETE',
                old.id,
                old.kind,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;

/* Status (Concept Status) */

CREATE TABLE status
       (id INTEGER PRIMARY KEY ASC,
        status TEXT NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP);


CREATE TABLE status_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        id_old INTEGER, id_new INTEGER,
        status_old TEXT, status_new TEXT,
        u_old INTEGER, u_new INTEGER NOT NULL,
        t_old TIMESTAMP, t_new TIMESTAMP);

CREATE TRIGGER status_insert AFTER INSERT ON status
       BEGIN
       INSERT INTO status_log  (action,
                               id_new,
                               status_new,
                               u_new,
                               t_new)

       VALUES ('INSERT',
               new.id,
               new.status,
               new.u,
               new.t);
       END;

CREATE TRIGGER status_update AFTER UPDATE ON status
       BEGIN
       INSERT INTO status_log  (action,
                                id_old, id_new,
                                status_old, status_new,
                                u_old, u_new,
                                t_old, t_new)

       VALUES ('UPDATE',
                old.id, new.id,
                old.status, new.status,
                old.u, new.u,
                old.t, new.t);
       END;

CREATE TRIGGER status_delete AFTER DELETE ON status
       BEGIN
       INSERT INTO status_log  (action,
                                id_old,
                                status_old,
                                u_old, u_new,
                                t_old, t_new)

       VALUES ('DELETE',
                old.id,
                old.status,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;



/* Projects */
CREATE TABLE proj
       (id INTEGER PRIMARY KEY ASC,
        code TEXT NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE proj_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        id_old INTEGER, id_new INTEGER,
        code_old TEXT, code_new TEXT,
        u_old INTEGER, u_new INTEGER NOT NULL,
        t_old TIMESTAMP, t_new TIMESTAMP);

CREATE TRIGGER proj_insert AFTER INSERT ON proj
       BEGIN
       INSERT INTO proj_log  (action,
                              id_new,
                              code_new,
                              u_new,
                              t_new)

       VALUES ('INSERT',
               new.id,
               new.code,
               new.u,
               new.t);
       END;

CREATE TRIGGER proj_update AFTER UPDATE ON proj
       BEGIN
       INSERT INTO proj_log  (action,
                              id_old, id_new,
                              code_old, code_new,
                              u_old, u_new,
                              t_old, t_new)

       VALUES ('UPDATE',
                old.id, new.id,
                old.code, new.code,
                old.u, new.u,
                old.t, new.t);
       END;

CREATE TRIGGER proj_delete AFTER DELETE ON proj
       BEGIN
       INSERT INTO proj_log  (action,
                              id_old,
                              code_old,
                              u_old, u_new,
                              t_old, t_new)

       VALUES ('DELETE',
                old.id,
                old.code,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;




/* Sources (aka Projects+Version) */

CREATE TABLE src
       (id INTEGER PRIMARY KEY ASC,
        proj_id INTEGER NOT NULL,
        version TEXT NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(proj_id) REFERENCES proj(id));

CREATE UNIQUE INDEX proj_id_ver_index ON src(proj_id, version);


CREATE TABLE src_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        id_old INTEGER, id_new INTEGER,
        proj_id_old INTEGER, proj_id_new INTEGER,
        version_old TEXT, version_new TEXT,
        u_old INTEGER, u_new INTEGER NOT NULL,
        t_old TIMESTAMP, t_new TIMESTAMP);

CREATE TRIGGER src_insert AFTER INSERT ON src
       BEGIN
       INSERT INTO src_log  (action,
                             id_new,
        		     proj_id_new,
			     version_new,
                             u_new,
                             t_new)

       VALUES ('INSERT',
               new.id,
               new.proj_id,
               new.version,
               new.u,
               new.t);
       END;

CREATE TRIGGER src_update AFTER UPDATE ON src
       BEGIN
       INSERT INTO src_log  (action,
                             id_old, id_new,
		             proj_id_old, proj_id_new,
			     version_old, version_new,
                             u_old, u_new,
                             t_old, t_new)

       VALUES ('UPDATE',
                old.id, new.id,
                old.proj_id, new.proj_id,
                old.version, new.version,
                old.u, new.u,
                old.t, new.t);
       END;

CREATE TRIGGER src_delete AFTER DELETE ON src
       BEGIN
       INSERT INTO src_log  (action,
                             id_old,
		             proj_id_old,
			     version_old,
                             u_old, u_new,
                             t_old, t_new)

       VALUES ('DELETE',
                old.id,
                old.proj_id,
                old.version,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;

CREATE TABLE src_meta
       (src_id INTEGER,
        attr TEXT NOT NULL,
        val TEXT NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(src_id) REFERENCES src(id));

CREATE INDEX src_meta_src_id_index ON src_meta (src_id);

CREATE TABLE src_meta_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        src_id_old INTEGER, src_id_new INTEGER,
        attr_old TEXT, attr_new TEXT,
        val_old TEXT, val_new TEXT,
        u_old INTEGER, u_new INTEGER NOT NULL,
        t_old TIMESTAMP, t_new TIMESTAMP);

CREATE TRIGGER src_meta_insert AFTER INSERT ON src_meta
       BEGIN
       INSERT INTO src_meta_log  (action,
                                  src_id_new,
                                  attr_new,
                                  val_new,
                                  u_new,
                                  t_new)

       VALUES ('INSERT',
               new.src_id,
               new.attr,
               new.val,
               new.u,
               new.t);
       END;

CREATE TRIGGER src_meta_update AFTER UPDATE ON src_meta
       BEGIN
       INSERT INTO src_meta_log  (action,
                                   src_id_old, src_id_new,
                                   attr_old, attr_new,
                                   val_old, val_new,
                                   u_old, u_new,
                                   t_old, t_new)

       VALUES ('UPDATE',
                old.src_id, new.src_id,
                old.attr, new.attr,
                old.val, new.val,
                old.u, new.u,
                old.t, new.t);
       END;

CREATE TRIGGER src_meta_delete AFTER DELETE ON src_meta
       BEGIN
       INSERT INTO src_meta_log  (action,
                                   src_id_old,
                                   attr_old,
                                   val_old,
                                   u_old, u_new,
                                   t_old, t_new)

       VALUES ('DELETE',
                old.src_id,
                old.attr,
                old.val,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;



/* ^^^^^^^^^^^^^^^ UNTIL HERE IT SHOULD BE SHARED BETWEEN CILI AND OMW ^^^^^^^^^^^^^^^  */



/* ILI */

CREATE TABLE ili
       (id INTEGER PRIMARY KEY ASC,
        kind_id INTEGER NOT NULL,
        def TEXT NOT NULL,
        status_id INTEGER NOT NULL,
        superseded_by_id INTEGER,
        origin_src_id INTEGER NOT NULL,
        src_key TEXT NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(origin_src_id) REFERENCES src(id),
	FOREIGN KEY(kind_id) REFERENCES kind(id),
	FOREIGN KEY(superseded_by_id) REFERENCES ili(id),
	FOREIGN KEY(status_id) REFERENCES status(id));

CREATE TABLE ili_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        id_old INTEGER, id_new INTEGER,
        kind_id_old INTEGER, kind_id_new INTEGER,
        def_old TEXT, def_new TEXT,
        status_id_old INTEGER, status_id_new INTEGER,
        superseded_by_id_old INTEGER, superseded_by_id_new INTEGER,
        origin_src_id_old INTEGER, origin_src_id_new INTEGER,
        src_key_old TEXT, src_key_new TEXT,
        u_old INTEGER, u_new INTEGER NOT NULL,
        t_old TIMESTAMP, t_new TIMESTAMP);

CREATE TRIGGER ili_insert AFTER INSERT ON ili
       BEGIN
       INSERT INTO ili_log  (action,
                             id_new,
                             kind_id_new,
			     def_new,
			     status_id_new,
			     superseded_by_id_new,
			     origin_src_id_new,
			     src_key_new,
                             u_new,
                             t_new)

       VALUES ('INSERT',
               new.id,
               new.kind_id,
               new.def,
               new.status_id,
               new.superseded_by_id,
               new.origin_src_id,
               new.src_key,
               new.u,
               new.t);
       END;

CREATE TRIGGER ili_update AFTER UPDATE ON ili
       BEGIN
       INSERT INTO ili_log  (action,
                             id_old, id_new,
                             kind_id_old, kind_id_new,
			     def_old, def_new,
			     status_id_old, status_id_new,
			     superseded_by_id_old, superseded_by_id_new,
			     origin_src_id_old, origin_src_id_new,
			     src_key_old, src_key_new,
                             u_old, u_new,
                             t_old, t_new)

       VALUES ('UPDATE',
                old.id, new.id,
                old.kind_id, new.kind_id,
               	old.def, new.def,
                old.status_id, new.status_id,
               	old.superseded_by_id, new.superseded_by_id,
               	old.origin_src_id, new.origin_src_id,
               	old.src_key, new.src_key,
                old.u, new.u,
                old.t, new.t);
       END;

CREATE TRIGGER ili_delete AFTER DELETE ON ili
       BEGIN
       INSERT INTO ili_log  (action,
                             id_old,
                             kind_id_old,
			     def_old,
			     status_id_old,
			     superseded_by_id_old,
			     origin_src_id_old,
			     src_key_old,
                             u_old, u_new,
                             t_old, t_new)

       VALUES ('DELETE',
                old.id,
		old.kind_id,
               	old.def,
               	old.status_id,
               	old.superseded_by_id,
               	old.origin_src_id,
               	old.src_key,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;

/* ILI Concept Comments */

CREATE TABLE ili_com
       (id INTEGER PRIMARY KEY ASC,
        ili_id INTEGER NOT NULL,
        com TEXT NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(ili_id) REFERENCES ili(id));

CREATE TABLE ili_com_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        id_old INTEGER, id_new INTEGER,
        ili_id_old INTEGER, ili_id_new INTEGER,
        com_old TEXT, com_new TEXT,
        u_old INTEGER, u_new INTEGER NOT NULL,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER ili_com_insert AFTER INSERT ON ili_com
       BEGIN
       INSERT INTO ili_com_log  (action,
				 id_new,
                                 ili_id_new,
                                 com_new,
                                 u_new,
                                 t_new)

       VALUES ('INSERT',
       	       new.id,
               new.ili_id,
               new.com,
               new.u,
               new.t);
       END;

CREATE TRIGGER ili_com_update AFTER UPDATE ON ili_com
       BEGIN
       INSERT INTO ili_com_log  (action,
                                 id_old, id_new,
                                 ili_id_old, ili_id_new,
                                 com_old, com_new,
                                 u_old, u_new,
                                 t_old, t_new)

       VALUES ('UPDATE',
                old.id, new.id,
                old.ili_id, new.ili_id,
                old.com, new.com,
                old.u, new.u,
                old.t, new.t);
       END;

CREATE TRIGGER ili_com_delete AFTER DELETE ON ili_com
       BEGIN
       INSERT INTO ili_com_log  (action,
                                 id_old,
                                 ili_id_old,
                                 com_old,
                                 u_old, u_new,
                                 t_old, t_new)

       VALUES ('DELETE',
                old.id,
                old.ili_id,
                old.com,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;


/* ILI Concept Rating */

CREATE TABLE ili_rating
       (id INTEGER PRIMARY KEY ASC,
        ili_id INTEGER NOT NULL,
        rating INTEGER NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(ili_id) REFERENCES ili(id));

CREATE UNIQUE INDEX id_user_index ON ili_rating (ili_id, u);


CREATE TABLE ili_rating_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        id_old INTEGER, id_new INTEGER,
        ili_id_old INTEGER, ili_id_new INTEGER,
        rating_old TEXT, rating_new TEXT,
        u_old INTEGER, u_new INTEGER NOT NULL,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER ili_rating_insert AFTER INSERT ON ili_rating
       BEGIN
       INSERT INTO ili_rating_log (action,
				   id_new,
                                   ili_id_new,
                                   rating_new,
                                   u_new,
                                   t_new)

       VALUES ('INSERT',
       	       new.id,
               new.ili_id,
               new.rating,
               new.u,
               new.t);
       END;

CREATE TRIGGER ili_rating_update AFTER UPDATE ON ili_rating
       BEGIN
       INSERT INTO ili_rating_log  (action,
                                    id_old, id_new,
                                     ili_id_old, ili_id_new,
                           	     rating_old, rating_new,
                                     u_old, u_new,
                                     t_old, t_new)

       VALUES ('UPDATE',
                old.id, new.id,
                old.ili_id, new.ili_id,
                old.rating, new.rating,
                old.u, new.u,
                old.t, new.t);
       END;

CREATE TRIGGER ili_rating_delete AFTER DELETE ON ili_rating
       BEGIN
       INSERT INTO ili_rating_log  (action,
                                   id_old,
                        	   ili_id_old,
                                   rating_old,
                                   u_old, u_new,
                                   t_old, t_new)

       VALUES ('DELETE',
                old.id,
                old.ili_id,
                old.rating,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;



/* ^^^^^^^^^^^^^^^ UNTIL HERE IT SHOULD BE CILI ONLY ^^^^^^^^^^^^^^^  */





CREATE TABLE pos
       (id INTEGER PRIMARY KEY ASC,
        tag TEXT NOT NULL,
        def TEXT NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP);


CREATE TABLE pos_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        id_old INTEGER, id_new INTEGER,
        tag_old TEXT, tag_new TEXT,
        def_old TEXT, def_new TEXT,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER pos_insert AFTER INSERT ON pos
       BEGIN
       INSERT INTO pos_log  (action,
                             id_new,
                             tag_new,
                             def_new,
                             u_new,
                             t_new)

       VALUES ('INSERT',
               new.id,
               new.tag,
               new.def,
               new.u,
               new.t);
       END;


CREATE TRIGGER pos_update AFTER UPDATE ON pos
       BEGIN
       INSERT INTO pos_log  (action,
                             id_old, id_new,
                             tag_old, tag_new,
                             def_old, def_new,
                             u_old, u_new,
                             t_old, t_new)

       VALUES ('UPDATE',
                old.id, new.id,
                old.tag, new.tag,
                old.def, new.def,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER pos_delete AFTER DELETE ON pos
       BEGIN
       INSERT INTO pos_log  (action,
                             id_old,
                             tag_old,
                             def_old,
                             u_old, u_new,
                             t_old, t_new)

       VALUES ('DELETE',
                old.id,
                old.tag,
                old.def,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;

/* Synset Relations' List*/

CREATE TABLE ssrel
       (id INTEGER PRIMARY KEY ASC,
        rel TEXT NOT NULL,
        def TEXT NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP);


CREATE TABLE ssrel_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        id_old INTEGER, id_new INTEGER,
        rel_old TEXT, rel_new TEXT,
        def_old TEXT, def_new TEXT,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER ssrel_insert AFTER INSERT ON ssrel
       BEGIN
       INSERT INTO ssrel_log  (action,
                               id_new,
                               rel_new,
                               def_new,
                               u_new,
                               t_new)

       VALUES ('INSERT',
               new.id,
               new.rel,
               new.def,
               new.u,
               new.t);
       END;


CREATE TRIGGER ssrel_update AFTER UPDATE ON ssrel
       BEGIN
       INSERT INTO ssrel_log  (action,
                               id_old, id_new,
                               rel_old, rel_new,
                               def_old, def_new,
                               u_old, u_new,
                               t_old, t_new)

       VALUES ('UPDATE',
                old.id, new.id,
                old.rel, new.rel,
                old.def, new.def,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER ssrel_delete AFTER DELETE ON ssrel
       BEGIN
       INSERT INTO ssrel_log  (action,
                               id_old,
                               rel_old,
                               def_old,
                               u_old, u_new,
                               t_old, t_new)

       VALUES ('DELETE',
                old.id,
                old.rel,
                old.def,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;


/* Sense Relations*/

CREATE TABLE srel
       (id INTEGER PRIMARY KEY ASC,
        rel TEXT NOT NULL,
        def TEXT NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP);


CREATE TABLE srel_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        id_old INTEGER, id_new INTEGER,
        rel_old TEXT, rel_new TEXT,
        def_old TEXT, def_new TEXT,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER srel_insert AFTER INSERT ON srel
       BEGIN
       INSERT INTO srel_log  (action,
                              id_new,
                              rel_new,
                              def_new,
                              u_new,
                              t_new)

       VALUES ('INSERT',
               new.id,
               new.rel,
               new.def,
               new.u,
               new.t);
       END;


CREATE TRIGGER srel_update AFTER UPDATE ON srel
       BEGIN
       INSERT INTO srel_log  (action,
                              id_old, id_new,
                              rel_old, rel_new,
                              def_old, def_new,
                              u_old, u_new,
                              t_old, t_new)

       VALUES ('UPDATE',
                old.id, new.id,
                old.rel, new.rel,
                old.def, new.def,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER srel_delete AFTER DELETE ON srel
       BEGIN
       INSERT INTO srel_log  (action,
                              id_old,
                              rel_old,
                              def_old,
                              u_old, u_new,
                              t_old, t_new)

       VALUES ('DELETE',
                old.id,
                old.rel,
                old.def,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;



/* Synsets */

CREATE TABLE ss
       (id INTEGER PRIMARY KEY ASC,
        ili_id INTEGER,
        pos_id INTEGER NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(pos_id) REFERENCES pos(id));

CREATE UNIQUE INDEX ssid_iliid_index ON ss (id, ili_id);

CREATE TABLE ss_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        id_old INTEGER, id_new INTEGER,
        ili_id_old INTEGER, ili_id_new INTEGER,
        pos_id_old INTEGER, pos_id_new INTEGER,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER ss_insert AFTER INSERT ON ss
       BEGIN
       INSERT INTO ss_log  (action,
                            id_new,
                            ili_id_new,
                            pos_id_new,
                            u_new,
                            t_new)

       VALUES ('INSERT',
               new.id,
               new.ili_id,
               new.pos_id,
               new.u,
               new.t);
       END;


CREATE TRIGGER ss_update AFTER UPDATE ON ss
       BEGIN
       INSERT INTO ss_log  (action,
                            id_old, id_new,
                            ili_id_old, ili_id_new,
                            pos_id_old, pos_id_new,
                            u_old, u_new,
                            t_old, t_new)

       VALUES ('UPDATE',
                old.id, new.id,
                old.ili_id, new.ili_id,
                old.pos_id, new.pos_id,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER ss_delete AFTER DELETE ON ss
       BEGIN
       INSERT INTO ss_log  (action,
                            id_old,
                            ili_id_old,
                            pos_id_old,
                            u_old, u_new,
                            t_old, t_new)

       VALUES ('DELETE',
                old.id,
                old.ili_id,
                old.pos_id,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;



/* Synset Sources */

CREATE TABLE ss_src
       (ss_id INTEGER NOT NULL,
        src_id INTEGER NOT NULL,
        src_key TEXT NOT NULL,
        conf INTEGER NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    	FOREIGN KEY(ss_id) REFERENCES ss(id),
        FOREIGN KEY(src_id) REFERENCES src(id));


CREATE TABLE ss_src_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        ss_id_old INTEGER, ss_id_new INTEGER,
        src_id_old INTEGER, src_id_new INTEGER,
        src_key_old TEXT, src_key_new TEXT,
        conf_old INTEGER, conf_new INTEGER,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER ss_src_insert AFTER INSERT ON ss_src
       BEGIN
       INSERT INTO ss_src_log  (action,
                                ss_id_new,
                                src_id_new,
                                src_key_new,
                                conf_new,
                                u_new,
                                t_new)

       VALUES ('INSERT',
               new.ss_id,
               new.src_id,
               new.src_key,
               new.conf,
               new.u,
               new.t);
       END;


CREATE TRIGGER ss_src_update AFTER UPDATE ON ss_src
       BEGIN
       INSERT INTO ss_src_log  (action,
                                ss_id_old, ss_id_new,
                                src_id_old, src_id_new,
                                src_key_old, src_key_new,
                                conf_old, conf_new,
                                u_old, u_new,
                                t_old, t_new)

       VALUES ('UPDATE',
                old.ss_id, new.ss_id,
                old.src_id, new.src_id,
                old.src_key, new.src_key,
                old.conf, new.conf,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER ss_src_delete AFTER DELETE ON ss_src
       BEGIN
       INSERT INTO ss_src_log  (action,
                                ss_id_old,
                                src_id_old,
                                src_key_old,
                                conf_old,
                                u_old, u_new,
                                t_old, t_new)

       VALUES ('DELETE',
                old.ss_id,
                old.src_id,
                old.src_key,
                old.conf,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;





/* Forms (Word Forms) */

CREATE TABLE f
       (id INTEGER PRIMARY KEY ASC,
        lang_id INTEGER NOT NULL,
        pos_id INTEGER NOT NULL,
        lemma TEXT NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(lang_id) REFERENCES lang(id),
        FOREIGN KEY(pos_id) REFERENCES pos(id));

CREATE TABLE f_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        id_old INTEGER, id_new INTEGER,
        lang_id_old INTEGER, lang_id_new INTEGER,
        pos_id_old INTEGER, pos_id_new INTEGER,
        lemma_old TEXT, lemma_new TEXT,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER f_insert AFTER INSERT ON f
       BEGIN
       INSERT INTO f_log  (action,
                           id_new,
                           lang_id_new,
                           pos_id_new,
                           lemma_new,
                           u_new,
                           t_new)

       VALUES ('INSERT',
               new.id,
               new.lang_id,
               new.pos_id,
               new.lemma,
               new.u,
               new.t);
       END;


CREATE TRIGGER f_update AFTER UPDATE ON f
       BEGIN
       INSERT INTO f_log  (action,
                           id_old, id_new,
                           lang_id_old, lang_id_new,
                           pos_id_old, pos_id_new,
                           lemma_old, lemma_new,
                           u_old, u_new,
                           t_old, t_new)

       VALUES ('UPDATE',
                old.id, new.id,
                old.lang_id, new.lang_id,
                old.pos_id, new.pos_id,
                old.lemma, new.lemma,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER f_delete AFTER DELETE ON f
       BEGIN
       INSERT INTO f_log  (action,
                           id_old,
                           lang_id_old,
                           pos_id_old,
                           lemma_old,
                           u_old, u_new,
                           t_old, t_new)

       VALUES ('DELETE',
                old.id,
                old.lang_id,
                old.pos_id,
                old.lemma,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;


/* Form Sources */

CREATE TABLE f_src
       (f_id INTEGER NOT NULL,
        src_id INTEGER NOT NULL,
        conf INTEGER NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(f_id) REFERENCES f(id),
        FOREIGN KEY(src_id) REFERENCES src(id));


CREATE TABLE f_src_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        f_id_old INTEGER, f_id_new INTEGER,
        src_id_old INTEGER, src_id_new INTEGER,
        conf_old INTEGER, conf_new INTEGER,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER f_src_insert AFTER INSERT ON f_src
       BEGIN
       INSERT INTO f_src_log  (action,
                               f_id_new,
                               src_id_new,
                               conf_new,
                               u_new,
                               t_new)

       VALUES ('INSERT',
               new.f_id,
               new.src_id,
               new.conf,
               new.u,
               new.t);
       END;


CREATE TRIGGER f_src_update AFTER UPDATE ON f_src
       BEGIN
       INSERT INTO f_src_log  (action,
                               f_id_old, f_id_new,
                               src_id_old, src_id_new,
                               conf_old, conf_new,
                               u_old, u_new,
                               t_old, t_new)

       VALUES ('UPDATE',
                old.f_id, new.f_id,
                old.src_id, new.src_id,
                old.conf, new.conf,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER f_src_delete AFTER DELETE ON f_src
       BEGIN
       INSERT INTO f_src_log  (action,
                               f_id_old,
                               src_id_old,
                               conf_old,
                               u_old, u_new,
                               t_old, t_new)

       VALUES ('DELETE',
                old.f_id,
                old.src_id,
                old.conf,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;


/* Form Meta Tags */

CREATE TABLE fmt
       (id INTEGER PRIMARY KEY ASC,
        tag TEXT NOT NULL,
        name TEXT NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP);


CREATE TABLE fmt_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        id_old INTEGER, id_new INTEGER,
        tag_old TEXT, tag_new TEXT,
        name_old TEXT, name_new TEXT,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER fmt_insert AFTER INSERT ON fmt
       BEGIN
       INSERT INTO fmt_log  (action,
                             id_new,
                             tag_new,
                             name_new,
                             u_new,
                             t_new)

       VALUES ('INSERT',
               new.id,
               new.tag,
               new.name,
               new.u,
               new.t);
       END;


CREATE TRIGGER fmt_update AFTER UPDATE ON fmt
       BEGIN
       INSERT INTO fmt_log  (action,
                             id_old, id_new,
                             tag_old, tag_new,
                             name_old, name_new,
                             u_old, u_new,
                             t_old, t_new)

       VALUES ('UPDATE',
                old.id, new.id,
                old.tag, new.tag,
                old.name, new.name,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER fmt_delete AFTER DELETE ON fmt
       BEGIN
       INSERT INTO fmt_log  (action,
                             id_old,
                             tag_old,
                             name_old,
                             u_old, u_new,
                             t_old, t_new)

       VALUES ('DELETE',
                old.id,
                old.tag,
                old.name,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;



/* Form Meta Labels */

CREATE TABLE fml
       (id INTEGER PRIMARY KEY ASC,
        label TEXT NOT NULL,
        name TEXT NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP);


CREATE TABLE fml_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        id_old INTEGER, id_new INTEGER,
        label_old TEXT, label_new TEXT,
        name_old TEXT, name_new TEXT,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER fml_insert AFTER INSERT ON fml
       BEGIN
       INSERT INTO fml_log  (action,
                             id_new,
                             label_new,
                             name_new,
                             u_new,
                             t_new)

       VALUES ('INSERT',
               new.id,
               new.label,
               new.name,
               new.u,
               new.t);
       END;


CREATE TRIGGER fml_update AFTER UPDATE ON fml
       BEGIN
       INSERT INTO fml_log  (action,
                             id_old, id_new,
                             label_old, label_new,
                             name_old, name_new,
                             u_old, u_new,
                             t_old, t_new)

       VALUES ('UPDATE',
                old.id, new.id,
                old.label, new.label,
                old.name, new.name,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER fml_delete AFTER DELETE ON fml
       BEGIN
       INSERT INTO fml_log  (action,
                             id_old,
                             label_old,
                             name_old,
                             u_old, u_new,
                             t_old, t_new)

       VALUES ('DELETE',
                old.id,
                old.label,
                old.name,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;



/* Form Meta
   Labels are not constrained because they can be interpreted as integers depending on the tag (i.e. frequency)
*/

CREATE TABLE fm
       (id INTEGER PRIMARY KEY ASC,
        f_id INTEGER NOT NULL,
        fmt_id INTEGER NOT NULL,
        fml_id INTEGER NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(f_id) REFERENCES f(id),
	FOREIGN KEY(fmt_id) REFERENCES fmt(id));

CREATE TABLE fm_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        id_old INTEGER, id_new INTEGER,
        f_id_old INTEGER, f_id_new INTEGER,
        fmt_id_old INTEGER, fmt_id_new INTEGER,
        fml_id_old INTEGER, fml_id_new INTEGER,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER fm_insert AFTER INSERT ON fm
       BEGIN
       INSERT INTO fm_log  (action,
                            id_new,
                            f_id_new,
                            fmt_id_new,
                            fml_id_new,
                            u_new,
                            t_new)

       VALUES ('INSERT',
               new.id,
               new.f_id,
               new.fmt_id,
               new.fml_id,
               new.u,
               new.t);
       END;


CREATE TRIGGER fm_update AFTER UPDATE ON fm
       BEGIN
       INSERT INTO fm_log  (action,
                            id_old, id_new,
                            f_id_old, f_id_new,
                            fmt_id_old, fmt_id_new,
                            fml_id_old, fml_id_new,
                            u_old, u_new,
                            t_old, t_new)

       VALUES ('UPDATE',
                old.id, new.id,
                old.f_id, new.f_id,
                old.fmt_id, new.fmt_id,
                old.fml_id, new.fml_id,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER fm_delete AFTER DELETE ON fm
       BEGIN
       INSERT INTO fm_log  (action,
                            id_old,
                            f_id_old,
                            fmt_id_old,
                            fml_id_old,
                            u_old, u_new,
                            t_old, t_new)

       VALUES ('DELETE',
                old.id,
                old.f_id,
                old.fmt_id,
                old.fml_id,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;




/* Form Meta Sources */

CREATE TABLE fm_src
       (fm_id INTEGER NOT NULL,
        src_id INTEGER NOT NULL,
        conf INTEGER NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(fm_id) REFERENCES fm(id),
        FOREIGN KEY(src_id) REFERENCES src(id));


CREATE TABLE fm_src_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        fm_id_old INTEGER, fm_id_new INTEGER,
        src_id_old INTEGER, src_id_new INTEGER,
        conf_old INTEGER, conf_new INTEGER,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER fm_src_insert AFTER INSERT ON fm_src
       BEGIN
       INSERT INTO fm_src_log  (action,
                                fm_id_new,
                                src_id_new,
                                conf_new,
                                u_new,
                                t_new)

       VALUES ('INSERT',
               new.fm_id,
               new.src_id,
               new.conf,
               new.u,
               new.t);
       END;


CREATE TRIGGER fm_src_update AFTER UPDATE ON fm_src
       BEGIN
       INSERT INTO fm_src_log  (action,
                                fm_id_old, fm_id_new,
                                src_id_old, src_id_new,
                                conf_old, conf_new,
                                u_old, u_new,
                                t_old, t_new)

       VALUES ('UPDATE',
                old.fm_id, new.fm_id,
                old.src_id, new.src_id,
                old.conf, new.conf,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER fm_src_delete AFTER DELETE ON fm_src
       BEGIN
       INSERT INTO fm_src_log  (action,
                                fm_id_old,
                                src_id_old,
                                conf_old,
                                u_old, u_new,
                                t_old, t_new)

       VALUES ('DELETE',
                old.fm_id,
                old.src_id,
                old.conf,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;



/* Words
   Words must link to a single canonical form to be displayed.
   Besides the canonical form, words can also link to other forms
   through the wf_link (word-form-link) table.
 */


CREATE TABLE w
       (id INTEGER PRIMARY KEY ASC,
        canon INTEGER NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(canon) REFERENCES f(id));

CREATE TABLE w_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        id_old INTEGER, id_new INTEGER,
        canon_old INTEGER, canon_new INTEGER,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER w_insert AFTER INSERT ON w
       BEGIN
       INSERT INTO w_log (action,
                          id_new,
                          canon_new,
                          u_new,
                          t_new)

       VALUES ('INSERT',
               new.id,
               new.canon,
               new.u,
               new.t);
       END;


CREATE TRIGGER w_update AFTER UPDATE ON w
       BEGIN
       INSERT INTO w_log (action,
                          id_old, id_new,
                          canon_old, canon_new,
                          u_old, u_new,
                          t_old, t_new)

       VALUES ('UPDATE',
                old.id, new.id,
                old.canon, new.canon,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER w_delete AFTER DELETE ON w
       BEGIN
       INSERT INTO w_log (action,
                          id_old,
                          canon_old,
                          u_old, u_new,
                          t_old, t_new)

       VALUES ('DELETE',
                old.id,
                old.canon,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;




/* Word Form Links
   This table substitutes complites word-form link and source table
   (since it doesn't enforce a primary key per link)
*/



CREATE TABLE wf_link
       (w_id INTEGER NOT NULL,
        f_id INTEGER NOT NULL,
        src_id INTEGER NOT NULL,
        conf INTEGER NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(w_id) REFERENCES w(id),
	FOREIGN KEY(f_id) REFERENCES f(id),
	FOREIGN KEY(src_id) REFERENCES src(id));

CREATE INDEX wf_link_w_id_index ON wf_link (w_id);
CREATE INDEX wf_link_f_id_index ON wf_link (f_id);


CREATE TABLE wf_link_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        w_id_old INTEGER, w_id_new INTEGER,
        f_id_old INTEGER, f_id_new INTEGER,
        src_id_old INTEGER, src_id_new INTEGER,
        conf_old INTEGER, conf_new INTEGER,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER wf_link_insert AFTER INSERT ON wf_link
       BEGIN
       INSERT INTO wf_link_log (action,
                                w_id_new,
                                f_id_new,
                                src_id_new,
                                conf_new,
                                u_new,
                                t_new)

       VALUES ('INSERT',
               new.w_id,
               new.f_id,
               new.src_id,
               new.conf,
               new.u,
               new.t);
       END;


CREATE TRIGGER wf_link_update AFTER UPDATE ON wf_link
       BEGIN
       INSERT INTO wf_link_log (action,
                                w_id_old, w_id_new,
                                f_id_old, f_id_new,
                                src_id_old, src_id_new,
                                conf_old, conf_new,
                                u_old, u_new,
                                t_old, t_new)

       VALUES ('UPDATE',
                old.w_id, new.w_id,
                old.f_id, new.f_id,
                old.src_id, new.src_id,
                old.conf, new.conf,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER wf_link_delete AFTER DELETE ON wf_link
       BEGIN
       INSERT INTO wf_link_log  (action,
                                 w_id_old,
                                 f_id_old,
                                 src_id_old,
                                 conf_old,
                                 u_old, u_new,
                                 t_old, t_new)

       VALUES ('DELETE',
                old.w_id,
                old.f_id,
                old.src_id,
                old.conf,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;





/* Senses  */

CREATE TABLE s
       (id INTEGER PRIMARY KEY ASC,
        ss_id INTEGER NOT NULL,
        w_id INTEGER NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(ss_id) REFERENCES ss(id),
        FOREIGN KEY(w_id) REFERENCES w(id));


CREATE TABLE s_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        id_old INTEGER, id_new INTEGER,
        ss_id_old INTEGER, ss_id_new INTEGER,
        w_id_old INTEGER, w_id_new INTEGER,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER s_insert AFTER INSERT ON s
       BEGIN
       INSERT INTO s_log  (action,
                           id_new,
                           ss_id_new,
                           w_id_new,
                           u_new,
                           t_new)

       VALUES ('INSERT',
               new.id,
               new.ss_id,
               new.w_id,
               new.u,
               new.t);
       END;


CREATE TRIGGER s_update AFTER UPDATE ON s
       BEGIN
       INSERT INTO s_log (action,
                          id_old, id_new,
                          ss_id_old, ss_id_new,
                          w_id_old, w_id_new,
                          u_old, u_new,
                          t_old, t_new)

       VALUES ('UPDATE',
                old.id, new.id,
                old.ss_id, new.ss_id,
                old.w_id, new.w_id,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER s_delete AFTER DELETE ON s
       BEGIN
       INSERT INTO s_log  (action,
                           id_old,
                           ss_id_old,
                           w_id_old,
                           u_old, u_new,
                           t_old, t_new)

       VALUES ('DELETE',
                old.id,
                old.ss_id,
                old.w_id,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;



/* Sense Sources */


CREATE TABLE s_src
       (s_id INTEGER NOT NULL,
        src_id INTEGER NOT NULL,
        conf INTEGER NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(s_id) REFERENCES s(id),
        FOREIGN KEY(src_id) REFERENCES src(id));


CREATE TABLE s_src_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        s_id_old INTEGER, s_id_new INTEGER,
        src_id_old INTEGER, src_id_new INTEGER,
        conf_old INTEGER, conf_new INTEGER,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER s_src_insert AFTER INSERT ON s_src
       BEGIN
       INSERT INTO s_src_log  (action,
                               s_id_new,
                               src_id_new,
                               conf_new,
                               u_new,
                               t_new)

       VALUES ('INSERT',
               new.s_id,
               new.src_id,
               new.conf,
               new.u,
               new.t);
       END;


CREATE TRIGGER s_src_update AFTER UPDATE ON s_src
       BEGIN
       INSERT INTO s_src_log  (action,
                               s_id_old, s_id_new,
                               src_id_old, src_id_new,
                               conf_old, conf_new,
                               u_old, u_new,
                               t_old, t_new)

       VALUES ('UPDATE',
                old.s_id, new.s_id,
                old.src_id, new.src_id,
                old.conf, new.conf,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER s_src_delete AFTER DELETE ON s_src
       BEGIN
       INSERT INTO s_src_log  (action,
                               s_id_old,
                               src_id_old,
                               conf_old,
                               u_old, u_new,
                               t_old, t_new)

       VALUES ('DELETE',
                old.s_id,
                old.src_id,
                old.conf,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;




/* Sense Meta Tags */


CREATE TABLE smt
       (id INTEGER PRIMARY KEY ASC,
        tag TEXT NOT NULL,
        name TEXT NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP);


CREATE TABLE smt_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        id_old INTEGER, id_new INTEGER,
        tag_old TEXT, tag_new TEXT,
        name_old TEXT, name_new TEXT,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER smt_insert AFTER INSERT ON smt
       BEGIN
       INSERT INTO smt_log  (action,
                             id_new,
                             tag_new,
                             name_new,
                             u_new,
                             t_new)

       VALUES ('INSERT',
               new.id,
               new.tag,
               new.name,
               new.u,
               new.t);
       END;


CREATE TRIGGER smt_update AFTER UPDATE ON smt
       BEGIN
       INSERT INTO smt_log  (action,
                             id_old, id_new,
                             tag_old, tag_new,
                             name_old, name_new,
                             u_old, u_new,
                             t_old, t_new)

       VALUES ('UPDATE',
                old.id, new.id,
                old.tag, new.tag,
                old.name, new.name,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER smt_delete AFTER DELETE ON smt
       BEGIN
       INSERT INTO smt_log  (action,
                             id_old,
                             tag_old,
                             name_old,
                             u_old, u_new,
                             t_old, t_new)

       VALUES ('DELETE',
                old.id,
                old.tag,
                old.name,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;



/* Sense Meta Labels */


CREATE TABLE sml
       (id INTEGER PRIMARY KEY ASC,
        label TEXT NOT NULL,
        name TEXT NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP);


CREATE TABLE sml_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        id_old INTEGER, id_new INTEGER,
        label_old TEXT, label_new TEXT,
        name_old TEXT, name_new TEXT,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER sml_insert AFTER INSERT ON sml
       BEGIN
       INSERT INTO sml_log  (action,
                             id_new,
                             label_new,
                             name_new,
                             u_new,
                             t_new)

       VALUES ('INSERT',
               new.id,
               new.label,
               new.name,
               new.u,
               new.t);
       END;


CREATE TRIGGER sml_update AFTER UPDATE ON sml
       BEGIN
       INSERT INTO sml_log  (action,
                             id_old, id_new,
                             label_old, label_new,
                             name_old, name_new,
                             u_old, u_new,
                             t_old, t_new)

       VALUES ('UPDATE',
                old.id, new.id,
                old.label, new.label,
                old.name, new.name,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER sml_delete AFTER DELETE ON sml
       BEGIN
       INSERT INTO sml_log  (action,
                             id_old,
                             label_old,
                             name_old,
                             u_old, u_new,
                             t_old, t_new)

       VALUES ('DELETE',
                old.id,
                old.label,
                old.name,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;


/* Sense Meta
   The meta label is not taken as a foreign keys because it can
   be used with open values, like sentiment.
*/


CREATE TABLE sm
       (id INTEGER PRIMARY KEY ASC,
        s_id INTEGER NOT NULL,
        smt_id INTEGER NOT NULL,
        sml_id INTEGER NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(s_id) REFERENCES s(id),
	FOREIGN KEY(smt_id) REFERENCES smt(id));

CREATE TABLE sm_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        id_old INTEGER, id_new INTEGER,
        s_id_old INTEGER, s_id_new INTEGER,
        smt_id_old INTEGER, smt_id_new INTEGER,
        sml_id_old INTEGER, sml_id_new INTEGER,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER sm_insert AFTER INSERT ON sm
       BEGIN
       INSERT INTO sm_log  (action,
                            id_new,
                            s_id_new,
                            smt_id_new,
                            sml_id_new,
                            u_new,
                            t_new)

       VALUES ('INSERT',
               new.id,
               new.s_id,
               new.smt_id,
               new.sml_id,
               new.u,
               new.t);
       END;


CREATE TRIGGER sm_update AFTER UPDATE ON sm
       BEGIN
       INSERT INTO sm_log  (action,
                            id_old, id_new,
                            s_id_old, s_id_new,
                            smt_id_old, smt_id_new,
                            sml_id_old, sml_id_new,
                            u_old, u_new,
                            t_old, t_new)

       VALUES ('UPDATE',
                old.id, new.id,
                old.s_id, new.s_id,
                old.smt_id, new.smt_id,
                old.sml_id, new.sml_id,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER sm_delete AFTER DELETE ON sm
       BEGIN
       INSERT INTO sm_log  (action,
                            id_old,
                            s_id_old,
                            smt_id_old,
                            sml_id_old,
                            u_old, u_new,
                            t_old, t_new)

       VALUES ('DELETE',
                old.id,
                old.s_id,
                old.smt_id,
                old.sml_id,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;



/* Sense  Meta Sources */


CREATE TABLE sm_src
       (sm_id INTEGER NOT NULL,
        src_id INTEGER NOT NULL,
        conf INTEGER NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(sm_id) REFERENCES s(id),
        FOREIGN KEY(src_id) REFERENCES src(id));


CREATE TABLE sm_src_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        sm_id_old INTEGER, sm_id_new INTEGER,
        src_id_old INTEGER, src_id_new INTEGER,
        conf_old INTEGER, conf_new INTEGER,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER sm_src_insert AFTER INSERT ON sm_src
       BEGIN
       INSERT INTO sm_src_log  (action,
                                sm_id_new,
                                src_id_new,
                                conf_new,
                                u_new,
                                t_new)

       VALUES ('INSERT',
               new.sm_id,
               new.src_id,
               new.conf,
               new.u,
               new.t);
       END;


CREATE TRIGGER sm_src_update AFTER UPDATE ON sm_src
       BEGIN
       INSERT INTO sm_src_log  (action,
                                sm_id_old, sm_id_new,
                                src_id_old, src_id_new,
                                conf_old, conf_new,
                                u_old, u_new,
                                t_old, t_new)

       VALUES ('UPDATE',
                old.sm_id, new.sm_id,
                old.src_id, new.src_id,
                old.conf, new.conf,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER sm_src_delete AFTER DELETE ON sm_src
       BEGIN
       INSERT INTO sm_src_log  (action,
                                sm_id_old,
                                src_id_old,
                                conf_old,
                                u_old, u_new,
                                t_old, t_new)

       VALUES ('DELETE',
                old.sm_id,
                old.src_id,
                old.conf,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;





/* Definitions
   Definitions can be in multiple languages
*/


CREATE TABLE def
       (id INTEGER PRIMARY KEY ASC,
        ss_id INTEGER NOT NULL,
        lang_id INTEGER NOT NULL,
        def TEXT NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(ss_id) REFERENCES ss(id),
	FOREIGN KEY(lang_id) REFERENCES lang(id));

CREATE UNIQUE INDEX ss_lang_def_index ON def (ss_id, lang_id, def);

CREATE TABLE def_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        id_old INTEGER, id_new INTEGER,
        ss_id_old INTEGER, ss_id_new INTEGER,
        lang_id_old INTEGER, lang_id_new INTEGER,
        def_old TEXT, def_new TEXT,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER def_insert AFTER INSERT ON def
       BEGIN
       INSERT INTO def_log  (action,
                             id_new,
                             ss_id_new,
                             lang_id_new,
                             def_new,
                             u_new,
                             t_new)

       VALUES ('INSERT',
               new.id,
               new.ss_id,
               new.lang_id,
               new.def,
               new.u,
               new.t);
       END;


CREATE TRIGGER def_update AFTER UPDATE ON def
       BEGIN
       INSERT INTO def_log  (action,
                             id_old, id_new,
                             ss_id_old, ss_id_new,
                             lang_id_old, lang_id_new,
                             def_old, def_new,
                             u_old, u_new,
                             t_old, t_new)

       VALUES ('UPDATE',
                old.id, new.id,
                old.ss_id, new.ss_id,
                old.lang_id, new.lang_id,
                old.def, new.def,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER def_delete AFTER DELETE ON def
       BEGIN
       INSERT INTO def_log  (action,
                             id_old,
                             ss_id_old,
                             lang_id_old,
                             def_old,
                             u_old, u_new,
                             t_old, t_new)

       VALUES ('DELETE',
                old.id,
                old.ss_id,
                old.lang_id,
                old.def,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;


/* Definition Sources */

CREATE TABLE def_src
       (def_id INTEGER NOT NULL,
        src_id INTEGER NOT NULL,
        conf INTEGER NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(def_id) REFERENCES def(id),
        FOREIGN KEY(src_id) REFERENCES src(id));


CREATE TABLE def_src_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        def_id_old INTEGER, def_id_new INTEGER,
        src_id_old INTEGER, src_id_new INTEGER,
        conf_old INTEGER, conf_new INTEGER,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER def_src_insert AFTER INSERT ON def_src
       BEGIN
       INSERT INTO def_src_log  (action,
                                 def_id_new,
                                 src_id_new,
                                 conf_new,
                                 u_new,
                                 t_new)

       VALUES ('INSERT',
               new.def_id,
               new.src_id,
               new.conf,
               new.u,
               new.t);
       END;


CREATE TRIGGER def_src_update AFTER UPDATE ON def_src
       BEGIN
       INSERT INTO def_src_log  (action,
                                 def_id_old, def_id_new,
                                 src_id_old, src_id_new,
                                 conf_old, conf_new,
                                 u_old, u_new,
                                 t_old, t_new)

       VALUES ('UPDATE',
                old.def_id, new.def_id,
                old.src_id, new.src_id,
                old.conf, new.conf,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER def_src_delete AFTER DELETE ON def_src
       BEGIN
       INSERT INTO def_src_log  (action,
                                 def_id_old,
                                 src_id_old,
                                 conf_old,
                                 u_old, u_new,
                                 t_old, t_new)

       VALUES ('DELETE',
                old.def_id,
                old.src_id,
                old.conf,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;



/* Sense Examples
   synset examples (ssexe) will be deprecated soon,
   sense examples are the default example
*/

CREATE TABLE exe
       (id INTEGER PRIMARY KEY ASC,
        s_id INTEGER NOT NULL,
        exe TEXT NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(s_id) REFERENCES s(id));

CREATE TABLE exe_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        id_old INTEGER, id_new INTEGER,
        s_id_old INTEGER, s_id_new INTEGER,
        exe_old TEXT, exe_new TEXT,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER exe_insert AFTER INSERT ON exe
       BEGIN
       INSERT INTO exe_log  (action,
                             id_new,
                             s_id_new,
                             exe_new,
                             u_new,
                             t_new)

       VALUES ('INSERT',
               new.id,
               new.s_id,
               new.exe,
               new.u,
               new.t);
       END;


CREATE TRIGGER exe_update AFTER UPDATE ON exe
       BEGIN
       INSERT INTO exe_log  (action,
                             id_old, id_new,
                             s_id_old, s_id_new,
                             exe_old, exe_new,
                             u_old, u_new,
                             t_old, t_new)

       VALUES ('UPDATE',
                old.id, new.id,
                old.s_id, new.s_id,
                old.exe, new.exe,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER exe_delete AFTER DELETE ON exe
       BEGIN
       INSERT INTO exe_log  (action,
                             id_old,
                             s_id_old,
                             exe_old,
                             u_old, u_new,
                             t_old, t_new)

       VALUES ('DELETE',
                old.id,
                old.s_id,
                old.exe,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;


/* Sense Example Sources */

CREATE TABLE exe_src
       (exe_id INTEGER NOT NULL,
        src_id INTEGER NOT NULL,
        conf INTEGER NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(exe_id) REFERENCES exe(id),
        FOREIGN KEY(src_id) REFERENCES src(id));


CREATE TABLE exe_src_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        exe_id_old INTEGER, exe_id_new INTEGER,
        src_id_old INTEGER, src_id_new INTEGER,
        conf_old INTEGER, conf_new INTEGER,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER exe_src_insert AFTER INSERT ON exe_src
       BEGIN
       INSERT INTO exe_src_log  (action,
                                 exe_id_new,
                                 src_id_new,
                                 conf_new,
                                 u_new,
                                 t_new)

       VALUES ('INSERT',
               new.exe_id,
               new.src_id,
               new.conf,
               new.u,
               new.t);
       END;


CREATE TRIGGER exe_src_update AFTER UPDATE ON exe_src
       BEGIN
       INSERT INTO exe_src_log  (action,
                                 exe_id_old, exe_id_new,
                                 src_id_old, src_id_new,
                                 conf_old, conf_new,
                                 u_old, u_new,
                                 t_old, t_new)

       VALUES ('UPDATE',
                old.exe_id, new.exe_id,
                old.src_id, new.src_id,
                old.conf, new.conf,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER exe_src_delete AFTER DELETE ON exe_src
       BEGIN
       INSERT INTO exe_src_log  (action,
                                 exe_id_old,
                                 src_id_old,
                                 conf_old,
                                 u_old, u_new,
                                 t_old, t_new)

       VALUES ('DELETE',
                old.exe_id,
                old.src_id,
                old.conf,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;



/* Synset Examples */


CREATE TABLE ssexe
       (id INTEGER PRIMARY KEY ASC,
        ss_id INTEGER NOT NULL,
        lang_id INTEGER NOT NULL,
        ssexe TEXT NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(ss_id) REFERENCES ss(id),
	FOREIGN KEY(lang_id) REFERENCES lang(id));

CREATE TABLE ssexe_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        id_old INTEGER, id_new INTEGER,
        ss_id_old INTEGER, ss_id_new INTEGER,
        lang_id_old INTEGER, lang_id_new INTEGER,
        ssexe_old TEXT, ssexe_new TEXT,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER ssexe_insert AFTER INSERT ON ssexe
       BEGIN
       INSERT INTO ssexe_log  (action,
                               id_new,
                               ss_id_new,
                               lang_id_new,
                               ssexe_new,
                               u_new,
                               t_new)

       VALUES ('INSERT',
               new.id,
               new.ss_id,
               new.lang_id,
               new.ssexe,
               new.u,
               new.t);
       END;


CREATE TRIGGER ssexe_update AFTER UPDATE ON ssexe
       BEGIN
       INSERT INTO ssexe_log  (action,
                               id_old, id_new,
                               ss_id_old, ss_id_new,
                               lang_id_old, lang_id_new,
                               ssexe_old, ssexe_new,
                               u_old, u_new,
                               t_old, t_new)

       VALUES ('UPDATE',
                old.id, new.id,
                old.ss_id, new.ss_id,
                old.lang_id, new.lang_id,
                old.ssexe, new.ssexe,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER ssexe_delete AFTER DELETE ON ssexe
       BEGIN
       INSERT INTO ssexe_log  (action,
                               id_old,
                               ss_id_old,
                               lang_id_old,
                               ssexe_old,
                               u_old, u_new,
                               t_old, t_new)

       VALUES ('DELETE',
                old.id,
                old.ss_id,
                old.lang_id,
                old.ssexe,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;


/* Synset Example Sources */


CREATE TABLE ssexe_src
       (ssexe_id INTEGER NOT NULL,
        src_id INTEGER NOT NULL,
        conf INTEGER NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(ssexe_id) REFERENCES ssexe(id),
        FOREIGN KEY(src_id) REFERENCES src(id));


CREATE TABLE ssexe_src_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        ssexe_id_old INTEGER, ssexe_id_new INTEGER,
        src_id_old INTEGER, src_id_new INTEGER,
        conf_old INTEGER, conf_new INTEGER,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER ssexe_src_insert AFTER INSERT ON ssexe_src
       BEGIN
       INSERT INTO ssexe_src_log  (action,
                                   ssexe_id_new,
                                   src_id_new,
                                   conf_new,
                                   u_new,
                                   t_new)

       VALUES ('INSERT',
               new.ssexe_id,
               new.src_id,
               new.conf,
               new.u,
               new.t);
       END;


CREATE TRIGGER ssexe_src_update AFTER UPDATE ON ssexe_src
       BEGIN
       INSERT INTO ssexe_src_log  (action,
                                   ssexe_id_old, ssexe_id_new,
                                   src_id_old, src_id_new,
                                   conf_old, conf_new,
                                   u_old, u_new,
                                   t_old, t_new)

       VALUES ('UPDATE',
                old.ssexe_id, new.ssexe_id,
                old.src_id, new.src_id,
                old.conf, new.conf,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER ssexe_src_delete AFTER DELETE ON ssexe_src
       BEGIN
       INSERT INTO ssexe_src_log  (action,
                                   ssexe_id_old,
                                   src_id_old,
                                   conf_old,
                                   u_old, u_new,
                                   t_old, t_new)

       VALUES ('DELETE',
                old.ssexe_id,
                old.src_id,
                old.conf,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;




/* Synset Links */

CREATE TABLE sslink
       (id INTEGER PRIMARY KEY ASC,
        ss1_id INTEGER NOT NULL,
        ssrel_id INTEGER NOT NULL,
        ss2_id INTEGER NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(ss1_id) REFERENCES ss(id),
	FOREIGN KEY(ssrel_id) REFERENCES ssrel(id),
	FOREIGN KEY(ss2_id) REFERENCES ss(id));

CREATE UNIQUE INDEX ss1_rel_ss2_index ON sslink (ss1_id, ssrel_id, ss2_id);

CREATE TABLE sslink_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        id_old INTEGER, id_new INTEGER,
        ss1_id_old INTEGER, ss1_id_new INTEGER,
        ssrel_id_old INTEGER, ssrel_id_new INTEGER,
        ss2_id_old INTEGER, ss2_id_new INTEGER,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER sslink_insert AFTER INSERT ON sslink
       BEGIN
       INSERT INTO sslink_log  (action,
                                id_new,
                                ss1_id_new,
                                ssrel_id_new,
                                ss2_id_new,
                                u_new,
                                t_new)

       VALUES ('INSERT',
               new.id,
               new.ss1_id,
               new.ssrel_id,
               new.ss2_id,
               new.u,
               new.t);
       END;


CREATE TRIGGER sslink_update AFTER UPDATE ON sslink
       BEGIN
       INSERT INTO sslink_log  (action,
                                id_old, id_new,
                                ss1_id_old, ss1_id_new,
                                ssrel_id_old, ssrel_id_new,
                                ss2_id_old, ss2_id_new,
                                u_old, u_new,
                                t_old, t_new)

       VALUES ('UPDATE',
                old.id, new.id,
                old.ss1_id, new.ss2_id,
                old.ssrel_id, new.ssrel_id,
                old.ss2_id, new.ss2_id,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER sslink_delete AFTER DELETE ON sslink
       BEGIN
       INSERT INTO sslink_log  (action,
                                id_old,
                                ss1_id_old,
                                ssrel_id_old,
                                ss2_id_old,
                                u_old, u_new,
                                t_old, t_new)

       VALUES ('DELETE',
                old.id,
                old.ss1_id,
                old.ssrel_id,
                old.ss2_id,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;


/* Synset Link Sources */

CREATE TABLE sslink_src
       (sslink_id INTEGER NOT NULL,
        src_id INTEGER NOT NULL,
        conf INTEGER NOT NULL,
        lang_id INTEGER NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	    FOREIGN KEY(sslink_id) REFERENCES sslink(id),
        FOREIGN KEY(src_id) REFERENCES src(id),
        FOREIGN KEY(lang_id) REFERENCES lang(id));


CREATE TABLE sslink_src_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        sslink_id_old INTEGER, sslink_id_new INTEGER,
        src_id_old INTEGER, src_id_new INTEGER,
        conf_old INTEGER, conf_new INTEGER,
        lang_id_old INTEGER, lang_id_new INTEGER,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER sslink_src_insert AFTER INSERT ON sslink_src
       BEGIN
       INSERT INTO sslink_src_log  (action,
                                    sslink_id_new,
                                    src_id_new,
                                    conf_new,
                                    lang_id_new,
                                    u_new,
                                    t_new)

       VALUES ('INSERT',
               new.sslink_id,
               new.src_id,
               new.conf,
               new.lang_id,
               new.u,
               new.t);
       END;


CREATE TRIGGER sslink_src_update AFTER UPDATE ON sslink_src
       BEGIN
       INSERT INTO sslink_src_log  (action,
                                    sslink_id_old, sslink_id_new,
                                    src_id_old, src_id_new,
                                    conf_old, conf_new,
                                    lang_id_old, lang_id_new,
                                    u_old, u_new,
                                    t_old, t_new)

       VALUES ('UPDATE',
                old.sslink_id, new.sslink_id,
                old.src_id, new.src_id,
                old.conf, new.conf,
                old.lang_id, new.lang_id,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER sslink_src_delete AFTER DELETE ON sslink_src
       BEGIN
       INSERT INTO sslink_src_log  (action,
                                    sslink_id_old,
                                    src_id_old,
                                    conf_old,
                                    lang_id_old,
                                    u_old, u_new,
                                    t_old, t_new)

       VALUES ('DELETE',
                old.sslink_id,
                old.src_id,
                old.conf,
                old.lang_id,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;


/* Sense Links */

CREATE TABLE slink
       (id INTEGER PRIMARY KEY ASC,
        s1_id INTEGER NOT NULL,
        srel_id INTEGER NOT NULL,
        s2_id INTEGER NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(s1_id) REFERENCES s(id),
	FOREIGN KEY(srel_id) REFERENCES srel(id),
	FOREIGN KEY(s2_id) REFERENCES s(id));

CREATE TABLE slink_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        id_old INTEGER, id_new INTEGER,
        s1_id_old INTEGER, s1_id_new INTEGER,
        srel_id_old INTEGER, srel_id_new INTEGER,
        s2_id_old INTEGER, s2_id_new INTEGER,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER slink_insert AFTER INSERT ON slink
       BEGIN
       INSERT INTO slink_log  (action,
                               id_new,
                               s1_id_new,
                               srel_id_new,
                               s2_id_new,
                               u_new,
                               t_new)

       VALUES ('INSERT',
               new.id,
               new.s1_id,
               new.srel_id,
               new.s2_id,
               new.u,
               new.t);
       END;


CREATE TRIGGER slink_update AFTER UPDATE ON slink
       BEGIN
       INSERT INTO slink_log  (action,
                               id_old, id_new,
                               s1_id_old, s1_id_new,
                               srel_id_old, srel_id_new,
                               s2_id_old, s2_id_new,
                               u_old, u_new,
                               t_old, t_new)

       VALUES ('UPDATE',
                old.id, new.id,
                old.s1_id, new.s2_id,
                old.srel_id, new.srel_id,
                old.s2_id, new.s2_id,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER slink_delete AFTER DELETE ON slink
       BEGIN
       INSERT INTO slink_log  (action,
                               id_old,
                               s1_id_old,
                               srel_id_old,
                               s2_id_old,
                               u_old, u_new,
                               t_old, t_new)

       VALUES ('DELETE',
                old.id,
                old.s1_id,
                old.srel_id,
                old.s2_id,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;


/* Sense Link Sources */

CREATE TABLE slink_src
       (slink_id INTEGER NOT NULL,
        src_id INTEGER NOT NULL,
        conf INTEGER NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(slink_id) REFERENCES slink(id),
        FOREIGN KEY(src_id) REFERENCES src(id));


CREATE TABLE slink_src_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        slink_id_old INTEGER, slink_id_new INTEGER,
        src_id_old INTEGER, src_id_new INTEGER,
        conf_old INTEGER, conf_new INTEGER,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER slink_src_insert AFTER INSERT ON slink_src
       BEGIN
       INSERT INTO slink_src_log  (action,
                                   slink_id_new,
                                   src_id_new,
                                   conf_new,
                                   u_new,
                                   t_new)

       VALUES ('INSERT',
               new.slink_id,
               new.src_id,
               new.conf,
               new.u,
               new.t);
       END;


CREATE TRIGGER slink_src_update AFTER UPDATE ON slink_src
       BEGIN
       INSERT INTO slink_src_log  (action,
                                   slink_id_old, slink_id_new,
                                   src_id_old, src_id_new,
                                   conf_old, conf_new,
                                   u_old, u_new,
                                   t_old, t_new)

       VALUES ('UPDATE',
                old.slink_id, new.slink_id,
                old.src_id, new.src_id,
                old.conf, new.conf,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER slink_src_delete AFTER DELETE ON slink_src
       BEGIN
       INSERT INTO slink_src_log  (action,
                                   slink_id_old,
                                   src_id_old,
                                   conf_old,
                                   u_old, u_new,
                                   t_old, t_new)

       VALUES ('DELETE',
                old.slink_id,
                old.src_id,
                old.conf,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;


/* Sense-Synset Links */

CREATE TABLE ssslink
       (id INTEGER PRIMARY KEY ASC,
        s_id INTEGER NOT NULL,
        srel_id INTEGER NOT NULL,
        ss_id INTEGER NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(s_id) REFERENCES s(id),
	FOREIGN KEY(srel_id) REFERENCES srel(id),
	FOREIGN KEY(ss_id) REFERENCES ss(id));

CREATE TABLE ssslink_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        id_old INTEGER, id_new INTEGER,
        s_id_old INTEGER, s_id_new INTEGER,
        srel_id_old INTEGER, srel_id_new INTEGER,
        ss_id_old INTEGER, ss_id_new INTEGER,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER ssslink_insert AFTER INSERT ON ssslink
       BEGIN
       INSERT INTO ssslink_log  (action,
                                 id_new,
                                 s_id_new,
                                 srel_id_new,
                                 ss_id_new,
                                 u_new,
                                 t_new)

       VALUES ('INSERT',
               new.id,
               new.s_id,
               new.srel_id,
               new.ss_id,
               new.u,
               new.t);
       END;


CREATE TRIGGER ssslink_update AFTER UPDATE ON ssslink
       BEGIN
       INSERT INTO ssslink_log  (action,
                                 id_old, id_new,
                                 s_id_old, s_id_new,
                                 srel_id_old, srel_id_new,
                                 ss_id_old, ss_id_new,
                                 u_old, u_new,
                                 t_old, t_new)

       VALUES ('UPDATE',
                old.id, new.id,
                old.s_id, new.s_id,
                old.srel_id, new.srel_id,
                old.ss_id, new.ss_id,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER ssslink_delete AFTER DELETE ON ssslink
       BEGIN
       INSERT INTO ssslink_log  (action,
                                 id_old,
                                 s_id_old,
                                 srel_id_old,
                                 ss_id_old,
                                 u_old, u_new,
                                 t_old, t_new)

       VALUES ('DELETE',
                old.id,
                old.s_id,
                old.srel_id,
                old.ss_id,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;


/* Sense-Synset Link Sources */

CREATE TABLE ssslink_src
       (ssslink_id INTEGER NOT NULL,
        src_id INTEGER NOT NULL,
        conf INTEGER NOT NULL,
        lang_id INTEGER NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(ssslink_id) REFERENCES ssslink(id),
        FOREIGN KEY(src_id) REFERENCES src(id),
        FOREIGN KEY(lang_id) REFERENCES lang(id));


CREATE TABLE ssslink_src_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        ssslink_id_old INTEGER, ssslink_id_new INTEGER,
        src_id_old INTEGER, src_id_new INTEGER,
        conf_old INTEGER, conf_new INTEGER,
        lang_id_old INTEGER, lang_id_new INTEGER,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER ssslink_src_insert AFTER INSERT ON ssslink_src
       BEGIN
       INSERT INTO ssslink_src_log  (action,
                                     ssslink_id_new,
                                     src_id_new,
                                     conf_new,
                                     lang_id_new,
                                     u_new,
                                     t_new)

       VALUES ('INSERT',
               new.ssslink_id,
               new.src_id,
               new.conf,
               new.lang_id,
               new.u,
               new.t);
       END;


CREATE TRIGGER ssslink_src_update AFTER UPDATE ON ssslink_src
       BEGIN
       INSERT INTO ssslink_src_log  (action,
                                     ssslink_id_old, ssslink_id_new,
                                     src_id_old, src_id_new,
                                     conf_old, conf_new,
                                     lang_id_old, lang_id_new,
                                     u_old, u_new,
                                     t_old, t_new)

       VALUES ('UPDATE',
                old.ssslink_id, new.ssslink_id,
                old.src_id, new.src_id,
                old.conf, new.conf,
                old.lang_id, new.lang_id,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER ssslink_src_delete AFTER DELETE ON ssslink_src
       BEGIN
       INSERT INTO ssslink_src_log  (action,
                                     ssslink_id_old,
                                     src_id_old,
                                     conf_old,
                                     lang_id_old,
                                     u_old, u_new,
                                     t_old, t_new)

       VALUES ('DELETE',
                old.ssslink_id,
                old.src_id,
                old.conf,
                old.lang_id,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;


/* Resources - external to Wordnets */

CREATE TABLE resource
       (id INTEGER PRIMARY KEY ASC,
        code TEXT NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE resource_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        id_old INTEGER, id_new INTEGER,
        code_old TEXT, code_new TEXT,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER resource_insert AFTER INSERT ON resource
       BEGIN
       INSERT INTO resource_log  (action,
                                  id_new,
                                  code_new,
                                  u_new,
                                  t_new)

       VALUES ('INSERT',
               new.id,
               new.code,
               new.u,
               new.t);
       END;

CREATE TRIGGER resource_update AFTER UPDATE ON resource
       BEGIN
       INSERT INTO resource_log  (action,
                                  id_old, id_new,
                                  code_old, code_new,
                                  u_old, u_new,
                                  t_old, t_new)

       VALUES ('UPDATE',
                old.id, new.id,
                old.code, new.code,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER resource_delete AFTER DELETE ON resource
       BEGIN
       INSERT INTO resource_log  (action,
                                  id_old,
                                  code_old,
                                  u_old, u_new,
                                  t_old, t_new)

       VALUES ('DELETE',
                old.id,
                old.code,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;

/* Resources Meta */

CREATE TABLE resource_meta
       (resource_id INTEGER,
        attr TEXT NOT NULL,
        val TEXT NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

CREATE INDEX resource_meta_resource_id_index ON resource_meta (resource_id);


CREATE TABLE resource_meta_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        resource_id_old INTEGER, resource_id_new INTEGER,
        attr_old TEXT, attr_new TEXT,
        val_old TEXT, val_new TEXT,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER resource_meta_insert AFTER INSERT ON resource_meta
       BEGIN
       INSERT INTO resource_meta_log  (action,
                                       resource_id_new,
                                       attr_new,
                                       val_new,
                                       u_new,
                                       t_new)

       VALUES ('INSERT',
               new.resource_id,
               new.attr,
               new.val,
               new.u,
               new.t);
       END;


CREATE TRIGGER resource_meta_update AFTER UPDATE ON resource_meta
       BEGIN
       INSERT INTO resource_meta_log  (action,
                                       resource_id_old, resource_id_new,
                                       attr_old, attr_new,
                                       val_old, val_new,
                                       u_old, u_new,
                                       t_old, t_new)

       VALUES ('UPDATE',
                old.resource_id, new.resource_id,
                old.attr, new.attr,
                old.val, new.val,
                old.u, new.u,
                old.t, new.t);
       END;

CREATE TRIGGER resource_meta_delete AFTER DELETE ON resource_meta
       BEGIN
       INSERT INTO resource_meta_log  (action,
                                       resource_id_old,
                                       attr_old,
                                       val_old,
                                       u_old, u_new,
                                       t_old, t_new)

       VALUES ('DELETE',
                old.resource_id,
                old.attr,
                old.val,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;



/* Synset External Links */

CREATE TABLE ssxl
       (id INTEGER PRIMARY KEY ASC,
        ss_id INTEGER NOT NULL,
        resource_id INTEGER NOT NULL,
        x1 TEXT,
        x2 TEXT,
        x3 TEXT,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(ss_id) REFERENCES ss(id),
	FOREIGN KEY(resource_id) REFERENCES resource(id));

CREATE TABLE ssxl_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        id_old INTEGER, id_new INTEGER,
        ss_id_old INTEGER, ss_id_new INTEGER,
        resource_id_old INTEGER, resource_id_new INTEGER,
        x1_old TEXT, x1_new TEXT,
        x2_old TEXT, x2_new TEXT,
        x3_old TEXT, x3_new TEXT,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER ssxl_insert AFTER INSERT ON ssxl
       BEGIN
       INSERT INTO ssxl_log  (action,
                              id_new,
                              ss_id_new,
                              resource_id_new,
                              x1_new,
                              x2_new,
                              x3_new,
                              u_new,
                              t_new)

       VALUES ('INSERT',
               new.id,
               new.ss_id,
               new.resource_id,
               new.x1,
               new.x2,
               new.x3,
               new.u,
               new.t);
       END;


CREATE TRIGGER ssxl_update AFTER UPDATE ON ssxl
       BEGIN
       INSERT INTO ssxl_log  (action,
                              id_old, id_new,
                              ss_id_old, ss_id_new,
                              resource_id_old, resource_id_new,
                              x1_old, x1_new,
                              x2_old, x2_new,
                              x3_old, x3_new,
                              u_old, u_new,
                              t_old, t_new)

       VALUES ('UPDATE',
                old.id, new.id,
                old.ss_id, new.ss_id,
                old.resource_id, new.resource_id,
                old.x1, new.x1,
                old.x2, new.x2,
                old.x3, new.x3,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER ssxl_delete AFTER DELETE ON ssxl
       BEGIN
       INSERT INTO ssxl_log  (action,
                              id_old,
                              ss_id_old,
                              resource_id_old,
                              x1_old,
                              x2_old,
                              x3_old,
                              u_old, u_new,
                              t_old, t_new)

       VALUES ('DELETE',
                old.id,
                old.ss_id,
                old.resource_id,
                old.x1,
                old.x2,
                old.x3,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;


/* Sense External Links */

CREATE TABLE sxl
       (id INTEGER PRIMARY KEY ASC,
        s_id INTEGER NOT NULL,
        resource_id INTEGER NOT NULL,
        x1 TEXT,
        x2 TEXT,
        x3 TEXT,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(s_id) REFERENCES s(id),
	FOREIGN KEY(resource_id) REFERENCES resource(id));

CREATE TABLE sxl_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        id_old INTEGER, id_new INTEGER,
        s_id_old INTEGER, s_id_new INTEGER,
        resource_id_old INTEGER, resource_id_new INTEGER,
        x1_old TEXT, x1_new TEXT,
        x2_old TEXT, x2_new TEXT,
        x3_old TEXT, x3_new TEXT,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER sxl_insert AFTER INSERT ON sxl
       BEGIN
       INSERT INTO sxl_log  (action,
                             id_new,
                             s_id_new,
                             resource_id_new,
                             x1_new,
                             x2_new,
                             x3_new,
                             u_new,
                             t_new)

       VALUES ('INSERT',
               new.id,
               new.s_id,
               new.resource_id,
               new.x1,
               new.x2,
               new.x3,
               new.u,
               new.t);
       END;


CREATE TRIGGER sxl_update AFTER UPDATE ON sxl
       BEGIN
       INSERT INTO sxl_log  (action,
                             id_old, id_new,
                             s_id_old, s_id_new,
                             resource_id_old, resource_id_new,
                             x1_old, x1_new,
                             x2_old, x2_new,
                             x3_old, x3_new,
                             u_old, u_new,
                             t_old, t_new)

       VALUES ('UPDATE',
                old.id, new.id,
                old.s_id, new.s_id,
                old.resource_id, new.resource_id,
                old.x1, new.x1,
                old.x2, new.x2,
                old.x3, new.x3,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER sxl_delete AFTER DELETE ON sxl
       BEGIN
       INSERT INTO sxl_log  (action,
                             id_old,
                             s_id_old,
                             resource_id_old,
                             x1_old,
                             x2_old,
                             x3_old,
                             u_old, u_new,
                             t_old, t_new)

       VALUES ('DELETE',
                old.id,
                old.s_id,
                old.resource_id,
                old.x1,
                old.x2,
                old.x3,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;


/* Synset Comments */

CREATE TABLE ss_com
       (id INTEGER PRIMARY KEY ASC,
        ss_id INTEGER NOT NULL,
        com TEXT NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(ss_id) REFERENCES ss(id));

CREATE TABLE ss_com_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        id_old INTEGER, id_new INTEGER,
        ss_id_old INTEGER, ss_id_new INTEGER,
        com_old TEXT, com_new TEXT,
        u_old INTEGER, u_new INTEGER,
        t_old TIMESTAMP, t_new TIMESTAMP);


CREATE TRIGGER ss_com_insert AFTER INSERT ON ss_com
       BEGIN
       INSERT INTO ss_com_log  (action,
                                id_new,
                                ss_id_new,
                                com_new,
                                u_new,
                                t_new)

       VALUES ('INSERT',
               new.id,
               new.ss_id,
               new.com,
               new.u,
               new.t);
       END;

CREATE TRIGGER ss_com_update AFTER UPDATE ON ss_com
       BEGIN
       INSERT INTO ss_com_log  (action,
                                id_old, id_new,
                                ss_id_old, ss_id_new,
                                com_old, com_new,
                                u_old, u_new,
                                t_old, t_new)

       VALUES ('UPDATE',
                old.id, new.id,
                old.ss_id, new.ss_id,
                old.com, new.com,
                old.u, new.u,
                old.t, new.t);
       END;


CREATE TRIGGER ss_com_delete AFTER DELETE ON ss_com
       BEGIN
       INSERT INTO ss_com_log  (action,
                                id_old,
                                ss_id_old,
                                com_old,
                                u_old, u_new,
                                t_old, t_new)

       VALUES ('DELETE',
                old.id,
                old.ss_id,
                old.com,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;

/* labels for the synsets 
   not worth logging as they are often updated
   whenever frequencies change or languages are added
*/
CREATE TABLE label
       (id INTEGER PRIMARY KEY ASC,
        ss_id INTEGER NOT NULL,
        lang_id INTEGER NOT NULL,
        label TEXT NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(lang_id) REFERENCES lang(id),
        FOREIGN KEY(ss_id) REFERENCES ss(id));
