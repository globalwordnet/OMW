#!/usr/bin/env python3

import sqlite3
import logging
try:
    from statistics import harmonic_mean
except ImportError:
    import sys
    sys.exit('This script requires Python 3.6 or newer')

import gwadoc


def hmean(a, b):
    return harmonic_mean([a, b])

def main(args):
    con = sqlite3.connect(args.db)
    con.create_function('hmean', 2, hmean)

    c = con.cursor()

    freq_id = next(c.execute("SELECT id FROM smt WHERE tag='freq'"), [1])[0]
    c.execute('DROP TABLE IF EXISTS temp.s_freq')
    c.execute(
        '''
        CREATE TEMPORARY TABLE s_freq AS
          SELECT s.ss_id AS ss_id,
                 s.id AS s_id,
                 max(s_freq) AS freq
            FROM s
            JOIN (SELECT s_id,
                         sum(sml_id) AS s_freq
                    FROM sm
                   WHERE smt_id = ?
                   GROUP BY s_id)
              ON s_id = s.id
           GROUP BY s.ss_id
           ORDER BY s.ss_id ASC, freq DESC''',
        (freq_id,))
    # for row in c.execute('SELECT * FROM temp.s_freq'):
    #     print(row)
    idmap = dict(c.execute('SELECT rel, id FROM ssrel'))
    for rel in gwadoc.RELATIONS:
        if rel not in idmap:
            continue
        c.execute(
            '''
            SELECT ss1_id,
                   ss2_id,
                   hmean(f1.freq, f2.freq) AS score
              FROM (SELECT ss1_id, ss2_id
                      FROM sslink
                     WHERE ssrel_id = ?)
              JOIN temp.s_freq AS f1
                ON f1.ss_id = ss1_id
              JOIN temp.s_freq AS f2
                ON f2.ss_id = ss2_id
             ORDER BY score DESC
             LIMIT 10''',
            (idmap[rel],))
        for ss1, ss2, score in c.fetchall():
            label1 = c.execute(
                'SELECT label FROM label WHERE ss_id = ?',
                (ss1,)).fetchone()[0]
            label2 = c.execute(
                'SELECT label FROM label WHERE ss_id = ?',
                (ss2,)).fetchone()[0]

            print('{}\t{}\t{}\t{}'.format(rel, label1, label2, score))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('db', help='path to the database')
    parser.add_argument('lg', help='language for examples')
    logging.basicConfig(level=logging.DEBUG)
    args = parser.parse_args()
    main(args)
