import sqlite3
import sys, time

dbfile = "omw.db"
con = sqlite3.connect(dbfile)
curs = con.cursor()

print("\nYou should be testing over an empty table!")
print("Failure to comply will result in foreverness... \n")

commandlist = [
("""PRAGMA foreign_keys = 1;""",
 """Activating foreign key constraints"""),

("""INSERT INTO active_user (user_id)
    VALUES ('test-user-deleter');""",
 """Inserting active user"""),


# TESTING kind TABLE
("""INSERT INTO kind (kind, u)
    VALUES ('kind1', 'test-user');""",
 """Inserting in kind table"""),

("""UPDATE kind
    SET kind = 'kind2', u='test-user2'
    WHERE kind = 'kind1';""",
 """Updating in kind table"""),


# TESTING status TABLE
("""INSERT INTO status (status, u)
    VALUES ('status1', 'test-user');""",
 """Inserting in status table"""),

("""UPDATE status
    SET status = 'status2', u='test-user2'
    WHERE status = 'status1';""",
 """Updating in status table"""),



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

("""DELETE FROM src_meta WHERE attr = 'attr-test2' limit 5;""",
 """Deleting from src_meta table"""),


# TESTING ili TABLE
("""INSERT INTO ili (kind_id, def, status_id, origin_src_id, src_key, u)
    VALUES (1, 'def-test', 1, 1, 'src-key-test', 'test-user');""",
 """Inserting in ili table"""),

("""INSERT INTO ili (kind_id, def, status_id, origin_src_id, src_key, u)
    VALUES (1, 'def2-test', 1, 1, 'src-key2-test', 'test-user');""",
 """Inserting in ili table"""),

("""UPDATE ili
    SET superseded_by_id = 2, u='test-user2' WHERE id = 1;""",
 """Updating in ili table"""),


# TESTING ili_com TABLE
("""INSERT INTO ili_com (ili_id, com, u)
    VALUES (1, 'commentary-test', 'test-user');""",
 """Inserting in ili_com table"""),

("""UPDATE ili_com
    SET com = 'updated-commentary-test', u='test-user2' WHERE id = 1;""",
 """Updating in ili_com table"""),


# DELETING THINGS IN THE RIGHT ORDER
("""DELETE FROM ili_com;""",
 """Deleting from ili_com table"""),

("""DELETE FROM ili;""",
 """Deleting from ili table"""),

("""DELETE FROM kind;""",
 """Deleting from kind table"""),

("""DELETE FROM status;""",
 """Deleting from status table"""),

("""DELETE FROM src;""",
 """Deleting from src table"""),

("""DELETE FROM proj;""",
 """Deleting from proj table"""),

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
