#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict as dd
import sqlite3

from flask import g

from omw import app


def qs(ll):
    """return len(l) ?s sepeated by ','  to use in queries"""
    return ','.join('?' for l  in ll)


with app.app_context():

    ############################################################################
    # SET UP CONNECTIONS
    ############################################################################
    def connect_admin():
        return sqlite3.connect(app.config['ADMINDB'])

    # def connect_ili():
    #     return sqlite3.connect(ILIDB)

    def connect_omw():
        return sqlite3.connect(app.config['OMWDB'])

    def query_admin(query, args=(), one=False):
        cur = g.admin.execute(query, args)
        rv = [dict((cur.description[idx][0], value)
                   for idx, value in enumerate(row)) for row in cur.fetchall()]
        return (rv[0] if rv else None) if one else rv

    # def query_ili(query, args=(), one=False):
    #     cur = g.ili.execute(query, args)
    #     rv = [dict((cur.description[idx][0], value)
    #                for idx, value in enumerate(row)) for row in cur.fetchall()]
    #     return (rv[0] if rv else None) if one else rv

    def query_omw(query, args=(), one=False):
        cur = g.omw.execute(query, args)
        rv = [dict((cur.description[idx][0], value)
                   for idx, value in enumerate(row)) for row in cur.fetchall()]
        return (rv[0] if rv else None) if one else rv

    def query_omw_direct(query, args=(), one=False):
        cur = g.omw.execute(query, args)
        rv = cur.fetchall()
        return (rv[0] if rv else None) if one else rv
    

    def write_admin(query, args=(), one=False):
        cur = g.admin.cursor()
        cur.execute(query, args)
        lastid = cur.lastrowid
        g.admin.commit()
        return lastid

    # def write_ili(query, args=(), one=False):
    #     cur = g.ili.cursor()
    #     cur.execute(query, args)
    #     lastid = cur.lastrowid
    #     g.ili.commit()
    #     return lastid

    def write_omw(query, args=(), one=False):
        cur = g.omw.cursor()
        cur.execute(query, args)
        lastid = cur.lastrowid
        g.omw.commit()
        return lastid

    def blk_write_omw(query, args=(), one=False):
        cur = g.omw.cursor()
        cur.executemany(query, args)
        lastid = cur.lastrowid
        g.omw.commit()
        return lastid


    ############################################################################
    # ADMIN SQL
    ############################################################################

    def fetch_userid(userID):
        user = None
        for r in query_admin("""SELECT userID, password, 
                                       access_level, access_group 
                                FROM users
                                WHERE userID = ?""", [userID]):
            if r['userID']:
                user = (r['userID'], r['password'], 
                        r['access_level'], r['access_group'])
        return user


    def fetch_id_from_userid(userID):
        for r in query_admin("""SELECT id 
                                FROM users
                                WHERE userID = ?""", [userID]):
            return r['id']



    def fetch_allusers():
        users = dd()
        for r in query_admin("""SELECT * FROM users"""):
            users[r['id']] = r

        return users
