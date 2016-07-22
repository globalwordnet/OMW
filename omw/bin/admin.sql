/* Active User (used to record deletions) */

CREATE TABLE active_user
       (id INTEGER PRIMARY KEY ASC,
       user_id TEXT NOT NULL);


/* users */

CREATE TABLE users
       (id INTEGER PRIMARY KEY ASC,
        userID TEXT NOT NULL UNIQUE,
	full_name TEXT NOT NULL,
	password TEXT NOT NULL,
	email TEXT NOT NULL,
	access_level INTEGER NOT NULL,
	access_group TEXT NOT NULL,
	affiliation TEXT NOT NULL,
        u INTEGER NOT NULL,
        t TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE users_log
       (log_id INTEGER PRIMARY KEY ASC,
        action TEXT NOT NULL,
        id_old INTEGER, id_new INTEGER,
        userID_old TEXT, userID_new TEXT,
	full_name_old TEXT, full_name_new TEXT,
	password_old TEXT, password_new TEXT,
	email_old TEXT, email_new TEXT,
	access_level_old INTEGER, access_level_new INTEGER,
	access_group_old TEXT, access_group_new TEXT,
	affiliation_old TEXT, affiliation_new TEXT,
        u_old INTEGER, u_new INTEGER NOT NULL,
        t_old TIMESTAMP, t_new TIMESTAMP);

CREATE TRIGGER users_insert AFTER INSERT ON users
       BEGIN
       INSERT INTO users_log  (action,
                               id_new,
			       userID_new,
			       full_name_new,
			       password_new,
			       email_new,
			       access_level_new,
			       access_group_new,
			       affiliation_new,
                               u_new,
                               t_new)

       VALUES ('INSERT', 
               new.id,
	       new.userID,
	       new.full_name,
	       new.password,
	       new.email,
	       new.access_level,
	       new.access_group,
	       new.affiliation,
               new.u,
               new.t);
       END;

CREATE TRIGGER users_update AFTER UPDATE ON users
       BEGIN
       INSERT INTO users_log  (action,
                               id_old, id_new,
			       userID_old, userID_new,
			       full_name_old, full_name_new,
			       password_old, password_new,
			       email_old, email_new,
			       access_level_old, access_level_new,
			       access_group_old, access_group_new,
			       affiliation_old, affiliation_new,
                               u_old, u_new,
                               t_old, t_new)

       VALUES ('UPDATE',
                old.id, new.id,
		old.userID, new.userID,
		old.full_name, new.full_name,
		old.password, new.password,
		old.email, new.email,
		old.access_level, new.access_level,
		old.access_group, new.access_group,
		old.affiliation, new.affiliation,
                old.u, new.u,
                old.t, new.t);
       END;

CREATE TRIGGER users_delete AFTER DELETE ON users
       BEGIN
       INSERT INTO users_log  (action,
                               id_old,
			       userID_old,
			       full_name_old,
			       password_old,
			       email_old,
			       access_level_old,
			       access_group_old,
			       affiliation_old,
                               u_old, u_new,
                               t_old, t_new)

       VALUES ('DELETE', 
                old.id,
		old.userID,
		old.full_name,
		old.password,
		old.email,
		old.access_level,
		old.access_group,
		old.affiliation,
                old.u, (SELECT MAX(user_id) FROM active_user),
                old.t, CURRENT_TIMESTAMP);
       END;
