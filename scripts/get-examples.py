#!/usr/bin/env python3

import sqlite3
import logging

import gwadoc


DEFAULT_EN_ID = 1


def hmean(a, b):
    """Return the harmonic mean of two numbers."""
    return float(2*a*b) / (a + b)
    # return harmonic_mean([a, b])

def main(args):
    con = sqlite3.connect(args.db)
    con.create_function('hmean', 2, hmean)

    c = con.cursor()

    freq_id = next(c.execute("SELECT id FROM smt WHERE tag='freq'"), [1])[0]
    lang_id = next(c.execute("SELECT id FROM lang WHERE bcp47=?", (args.lg,)),
                   DEFAULT_EN_ID)[0]

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
    print('\t'.join(['relation', 'src-ili', 'src-ss', 'src-lbl',
                     'tgt-ili', 'tgt-ss', 'tgt-lbl', 'score']))
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
             LIMIT ?''',
            (idmap[rel], args.n))
        for ss1, ss2, score in c.fetchall():
            ili1 = c.execute(
                'SELECT ili_id FROM ss WHERE id=?',
                (ss1,)).fetchone()[0]
            ili2 = c.execute(
                'SELECT ili_id FROM ss WHERE id=?',
                (ss2,)).fetchone()[0]
            label1 = c.execute(
                'SELECT label FROM label WHERE ss_id = ? and lang_id = ?',
                (ss1, lang_id)).fetchone()[0]
            label2 = c.execute(
                'SELECT label FROM label WHERE ss_id = ? and lang_id = ?',
                (ss2, lang_id)).fetchone()[0]
            print('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}'
                  .format(rel, ili1, ss1, label1, ili2, ss2, label2, score))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('db', help='path to the database')
    parser.add_argument('lg', help='language for examples')
    parser.add_argument('-n', type=int,
                        help='get the top N examples per relation')
    logging.basicConfig(level=logging.DEBUG)
    args = parser.parse_args()
    main(args)
