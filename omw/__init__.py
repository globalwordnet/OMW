#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
from collections import (
    defaultdict as dd,
    OrderedDict as od
)
from math import log
import datetime

from flask import (
    Flask,
    render_template,
    g,
    request,
    redirect,
    url_for,
    send_from_directory,
    flash,
    jsonify,
    make_response,
    Markup,
    Response
)
from flask_login import (
    login_required,
    login_user,
    logout_user,
    current_user
)
from packaging.version import Version
import gwadoc
import networkx as nx
## profiler
#from werkzeug.contrib.profiler import ProfilerMiddleware
from omw.utils.utils import fetch_sorted_meta_by_version

app = Flask(__name__)
# Common configuration settings go here
app.config['REMEMBER_COOKIE_DURATION'] = datetime.timedelta(minutes=30)
# Installation-specific settings go in omw_config.py
app.config.from_object('config')

# Load these only after creating and configuring the app object
from .common_login import *
from .common_sql import *
from .omw_sql import *
from .wn_syntax import *
import omw.cli

## profiler
#app.config['PROFILE'] = True
#app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
#app.run(debug = True)


################################################################################
# LOGIN
################################################################################
login_manager.init_app(app)

@app.route("/login", methods=["GET", "POST"])
def login():
    """ This login function checks if the username & password
    match the admin.db; if the authentication is successful,
    it passes the id of the user into login_user() """

    if request.method == "POST" and \
       "username" in request.form and \
       "password" in request.form:
        username = request.form["username"]
        password = request.form["password"]

        user = User.get(username)

        # If we found a user based on username then compare that the submitted
        # password matches the password in the database. The password is stored
        # is a slated hash format, so you must hash the password before comparing it.
        if user and hash_pass(password) == user.password:
            login_user(user, remember=True)
            # FIXME! Get this to work properly...
            # return redirect(request.args.get("next") or url_for("index"))
            return redirect(url_for("index"))
        else:
            flash(u"Invalid username, please try again.")
    return render_template("login.html")

@app.route("/logout")
@login_required(role=0, group='open')
def logout():
    logout_user()
    return redirect(url_for("index"))
################################################################################



################################################################################
# SET UP CONNECTION WITH DATABASES
################################################################################

@app.before_request
def connect_dbs():
    connect_admin()
    connect_omw()

@app.teardown_appcontext
def teardown_dbs(exception):
    db = g.pop('admin', None)
    if db is not None:
        db.close()

    db = g.pop('omw', None)
    if db is not None:
        db.close()

################################################################################
# helper functions
################################################################################

def _get_cookie(name, default):
    if name in request.cookies:
        return request.cookies.get(name)
    else:
        return default
        



################################################################################
# AJAX REQUESTS
################################################################################
@app.route('/_thumb_up_id')
def thumb_up_id():
    user = fetch_id_from_userid(current_user.id)
    ili_id = request.args.get('ili_id', None)
    rate = 1
    r = rate_ili_id(ili_id, rate, user)

    counts, up_who, down_who = f_rate_summary([ili_id])
    html = """ <span style="color:green" title="Who voted up: {}">+{}</span><br>
               <span style="color:red"  title="Who voted down: {}">-{}</span>
           """.format(up_who[int(ili_id)], counts[int(ili_id)]['up'],
                      down_who[int(ili_id)], counts[int(ili_id)]['down'])
    return jsonify(result=html)


@app.route('/_thumb_down_id')
def thumb_down_id():
    user = fetch_id_from_userid(current_user.id)
    ili_id = request.args.get('ili_id', None)
    rate = -1
    r = rate_ili_id(ili_id, rate, user)

    counts, up_who, down_who = f_rate_summary([ili_id])
    html = """ <span style="color:green" title="Who voted up: {}">+{}</span><br>
               <span style="color:red"  title="Who voted down: {}">-{}</span>
           """.format(up_who[int(ili_id)], counts[int(ili_id)]['up'],
                      down_who[int(ili_id)], counts[int(ili_id)]['down'])
    return jsonify(result=html)


@app.route('/_comment_id')
def comment_id():
    user = fetch_id_from_userid(current_user.id)
    ili_id = request.args.get('ili_id', None)
    comment = request.args.get('comment', None)
    comment = str(Markup.escape(comment))
    dbinsert = comment_ili_id(ili_id, comment, user)
    return jsonify(result=dbinsert)


@app.route('/_detailed_id')
def detailed_id():
    ili_id = request.args.get('ili_id', None)
    rate_hist = fetch_rate_id([ili_id])
    comm_hist = fetch_comment_id([ili_id])
    users = fetch_allusers()

    r_html = ""
    for r, u, t in rate_hist[int(ili_id)]:
        r_html += '{} ({} &mdash; {}): {} <br>'.format(
            users[u]['full_name'], users[u]['userID'], t, r)

    c_html = ""
    for c, u, t in comm_hist[int(ili_id)]:
        c_html += '{} ({} &mdash; {}): {} <br>'.format(
            users[u]['full_name'], users[u]['userID'], t, c)

    html = """
    <td colspan="9">
    <div style="width: 49%; float:left;">
    <h6>Ratings</h6>
    {}</div>
    <div style="width: 49%; float:right;">
    <h6>Comments</h6>
    {}</div>
    </td>""".format(r_html, c_html)

    return jsonify(result=html)


@app.route('/_confirm_wn_upload')
def confirm_wn_upload_id():
    """
    Ingest the uploaded wordnet into the database and return a report.

    This happens when the user has confirmed they want to add a
    validated wordnet.
    """
    user = fetch_id_from_userid(current_user.id)
    fn = request.args.get('fn', None)
    report = ingest_wordnet(fn, user)
    for langid in report['lang_ids']:
        updateLabels(lang_id=langid)
    return jsonify(result=report)


@app.route('/_add_new_project')
def add_new_project():
    user = fetch_id_from_userid(current_user.id)
    proj = request.args.get('proj_code', None)
    proj = str(Markup.escape(proj))
    if user and proj:
        dbinsert = insert_new_project(proj, user)
        return jsonify(result=dbinsert)
    else:
        return jsonify(result=False)


@app.route("/_load_lang_selector",methods=["GET"])
def omw_lang_selector():
    selected_lang =  int(_get_cookie('selected_lang', 1))
    selected_lang2 =  int(_get_cookie('selected_lang2', 1))
    lang_id, lang_code = fetch_langs()
    html = '<select name="lang" style="font-size: 85%; width: 9em" required>'
    for lid in lang_id.keys():
        if selected_lang == lid:
            html += """<option value="{}" selected>{}</option>
                    """.format(lid, lang_id[lid][1])
        else:
            html += """<option value="{}">{}</option>
                    """.format(lid, lang_id[lid][1])
    html += '</select>'
    html += '<select name="lang2" style="font-size: 85%; width: 9em" required>'
    for lid in lang_id.keys():
        if selected_lang2 == lid:
            html += """<option value="{}" selected>{}</option>
                    """.format(lid, lang_id[lid][1])
        else:
            html += """<option value="{}">{}</option>
                    """.format(lid, lang_id[lid][1])
    html += '</select>'
    return jsonify(result=html)

@app.route('/_add_new_language')
def add_new_language():
    user = fetch_id_from_userid(current_user.id)
    bcp = request.args.get('bcp', None)
    bcp = str(Markup.escape(bcp))
    iso = request.args.get('iso', None)
    iso = str(Markup.escape(iso))
    name = request.args.get('name', None)
    name = str(Markup.escape(name))
    if bcp and name:
        dbinsert = insert_new_language(bcp, iso, name, user)
        return jsonify(result=dbinsert)
    else:
        return jsonify(result=False)


@app.route('/_load_proj_details')
def load_proj_details():
    proj_id = request.args.get('proj', 0)
    if proj_id:
        proj_id = int(proj_id)
    else:
        proj_id = None

    projs = fetch_proj()
    srcs = fetch_src()
    srcs_meta = fetch_src_meta()

    html = str()

    if proj_id:
        i = 0
        for src_id in srcs.keys():

            if srcs[src_id][0] == projs[proj_id]:
                i += 1
                html += "<br><p><b>Source {}: {}-{}</b></p>".format(i,
                        projs[proj_id],srcs[src_id][1])

                for attr, val in srcs_meta[src_id].items():
                    html += "<p style='margin-left: 40px'>"
                    html += attr + ": " + val
                    html += "</p>"


    return jsonify(result=html)



@app.route('/_load_min_omw_concept/<ss>')
@app.route('/_load_min_omw_concept_ili/<ili_id>')
def min_omw_concepts(ss=None, ili_id=None):

    if ili_id:
        ss_ids = f_ss_id_by_ili_id(ili_id)
    else:
        ss_ids = [ss]

    pos = fetch_pos()
    langs_id, langs_code = fetch_langs()
    ss, senses, defs, exes, links = fetch_ss_basic(ss_ids)
    ssrels = fetch_ssrel()
    selected_lang = int(_get_cookie('selected_lang', 1))
    labels = fetch_labels( selected_lang, set(senses.keys()))
    return jsonify(result=render_template('min_omw_concept.html',
                                          pos = pos,
                                          langs = langs_id,
                                          senses=senses,
                                          ss=ss,
                                          links=links,
                                          ssrels=ssrels,
                                          defs=defs,
                                          exes=exes,
                                          labels=labels))

@app.route('/_load_min_omw_sense/<sID>')
def min_omw_sense(sID=None):
    if sID:
        s_id=int(sID)
        langs_id, langs_code = fetch_langs()
        pos = fetch_pos()
        sense = fetch_sense(s_id)
        forms=fetch_forms(sense[3])
        selected_lang = int(_get_cookie('selected_lang', 1))
        labels= fetch_labels(selected_lang,[sense[4]])
        src_meta= fetch_src_meta()
        src_sid=fetch_src_for_s_id([s_id])
        sdefs = fetch_defs_by_sense([s_id])
        if selected_lang in sdefs[s_id]:
            sdef = sdefs[s_id][selected_lang] ## requested language
        else:
            sdef = sdefs[s_id][min(sdefs[s_id].keys())] ## a language
        if not sdef:
            sdef="no definition"
    
    #    return jsonify(result=render_template('omw_sense.html',
    return jsonify(result=render_template('min_omw_sense.html',
                                          s_id = s_id,
                                          sdef=sdef,
                                          sense = sense,
                                          forms=forms,
                                          langs = langs_id,
                                          pos = pos,
                                          labels = labels,
                                          src_sid = src_sid,
                                          src_meta = src_meta))


# l=lambda:dd(l)
# vr = l()  # wn-lmf validation report

# @app.route('/_report_val1')
# def report_val1():
#     filename = request.args.get('fn', None)
#     if filename:
#         vr1 = val1_DTD(current_user, filename)
#         vr.update(vr1)
#         if vr1['dtd_val'] == True:
#             html = "DTD PASSED"
#             return jsonify(result=html)
#         else:
#             html = "DTD FAILED" + '<br>' + vr['dtd_val_errors']
#             return jsonify(result=html)
#     else:
#         return jsonify(result="ERROR")

@app.route('/_report_val2', methods=['GET', 'POST'])
@login_required(role=0, group='open')
def report_val2():

    filename = request.args.get('fn', None)
    vr, filename, wn, wn_dtls = validateFile(current_user.id, filename)

    return jsonify(result=render_template('validation-report.html',
                    vr=vr, wn=wn, wn_dtls=wn_dtls, filename=filename))


    # validateFile()
    # filename = request.args.get('fn', None)
    # if filename:
    #     vr = val1_DTD(current_user, filename)
    #     if vr['dtd_val'] == True:
    #         html = "DTD PASSED"
    #         return jsonify(result=html)
    #     else:
    #         html = "DTD FAILED" + '<br>' + vr['dtd_val_errors']
    #         return jsonify(result=html)
    # else:
    #     return jsonify(result="ERROR")
    # return jsonify(result="TEST_VAL2")


################################################################################


################################################################################
# VIEWS
################################################################################
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/ili', methods=['GET', 'POST'])
def ili_welcome(name=None):
    return render_template('ili_welcome.html')

@app.route('/omw', methods=['GET', 'POST'])
def omw_welcome(name=None):
    projects = request.args.get('projects','current')
    lang_id, lang_code = fetch_langs()
    src_meta=fetch_src_meta()
    ### sort by language, project version (Newest first)
    src_meta_sorted = fetch_sorted_meta_by_version(projects, src_meta, lang_id, lang_code)

    return render_template('omw_welcome.html',
                           src_meta=src_meta_sorted,
                           lang_id=lang_id,
                           lang_code=lang_code,
                           licenses=licenses)

@app.route('/wordnet', methods=['GET', 'POST'])
def wordnet_license(name=None):
    return render_template('wordnet_license.html')

@app.route('/omw_wns', methods=['GET', 'POST'])
def omw_wns(name=None):
    projects = request.args.get('projects','current')
    src_meta=fetch_src_meta()
    stats = []
    lang_id, lang_code = fetch_langs()
    ### sort by language name (1), id, version (FIXME -- reverse version)
    src_sort=od()
    keys=list(src_meta.keys())
    keys.sort(key=lambda x: Version(src_meta[x]['version']),reverse=True) #Version
    keys.sort(key=lambda x: src_meta[x]['id']) #id 
    keys.sort(key=lambda x: lang_id[lang_code['code'][src_meta[x]['language']]][1]) #Language
    for k in keys:
        if projects=='current':  # only get the latest version
            if src_meta[k]['version'] != max((src_meta[i]['version'] for i in src_meta
                                              if src_meta[i]['id'] ==  src_meta[k]['id']),
                                             key=lambda x: Version(x)):
                continue
        stats.append((src_meta[k], fetch_src_id_stats(k)))
    return render_template('omw_wns.html',
                           stats=stats,
                           src_meta=src_meta,
                           lang_id=lang_id,
                           lang_code=lang_code,
                           licenses=licenses)

@app.route('/omw_stats', methods=['GET', 'POST'])
def omw_stats():
    """
    statistics about wordnet as a big graph
    """
    ### get language
    selected_lang =  int(_get_cookie('selected_lang', 1))
    ### get hypernym graph
    hypernym_dict=fetch_graph()
    G =  nx.DiGraph(hypernym_dict, name='OMW')
    info = nx.info(G).splitlines()
    
    cycles = list(nx.simple_cycles(G))
    ### get the synsets we need to label
    sss = []
    for c in cycles:
        for ss in c:
            sss.append(ss)
    label = fetch_labels(selected_lang, sss)
    return render_template('omw_stats.html',
                           info=info,
                           cycles=cycles,
                           label=label,
                           gwadoc=gwadoc)

@app.route("/useradmin",methods=["GET"])
@login_required(role=99, group='admin')
def useradmin():
    users = fetch_allusers()
    return render_template("useradmin.html", users=users)

@app.route("/langadmin",methods=["GET"])
@login_required(role=99, group='admin')
def langadmin():
    lang_id, lang_code = fetch_langs()
    return render_template("langadmin.html", langs=lang_id)

@app.route("/projectadmin",methods=["GET"])
@login_required(role=99, group='admin')
def projectadmin():
    projs = fetch_proj()
    srcs = fetch_src()
    srcs_by_proj = dd(list)
    for src_id in srcs:  # should be in the right order, as versions must go up
        srcs_by_proj[srcs[src_id][0]].append((srcs[src_id][1], src_id))
    srcs_meta = fetch_src_meta()
    return render_template("projectadmin.html",
                           projs=projs,
                           srcs_by_proj=srcs_by_proj,
                           srcs_meta=srcs_meta)

@app.route('/allconcepts', methods=['GET', 'POST'])
def allconcepts():
    ili, ili_defs = fetch_ili()
    rsumm, up_who, down_who = f_rate_summary(list(ili.keys()))
    return render_template('concept-list.html', ili=ili,
                           rsumm=rsumm, up_who=up_who, down_who=down_who)

@app.route('/temporary', methods=['GET', 'POST'])
def temporary():
    ili = fetch_ili_status(2)
    rsumm, up_who, down_who = f_rate_summary(list(ili.keys()))
    return render_template('concept-list.html', ili=ili,
                           rsumm=rsumm, up_who=up_who, down_who=down_who)


@app.route('/deprecated', methods=['GET', 'POST'])
def deprecated():
    ili = fetch_ili_status(0)
    rsumm, up_who, down_who = f_rate_summary(list(ili.keys()))
    return render_template('concept-list.html', ili=ili,
                           rsumm=rsumm, up_who=up_who, down_who=down_who)


@app.route('/ili/concepts/<c>', methods=['GET', 'POST'])
def concepts_ili(c=None):
    c = c.split(',')
    ili, ili_defs = fetch_ili(c)
    rsumm, up_who, down_who = f_rate_summary(list(ili.keys()))

    return render_template('concept-list.html', ili=ili,
                           rsumm=rsumm, up_who=up_who, down_who=down_who)


@app.route('/ili/search', methods=['GET', 'POST'])
@app.route('/ili/search/<q>', methods=['GET', 'POST'])
def search_ili(q=None):

    if q:
        query = q
    else:
        query = request.form['query']

    src_id = fetch_src()
    kind_id = fetch_kind()
    status_id = fetch_status()

    ili = dict()
    for c in query_omw("""SELECT * FROM ili WHERE def GLOB ?
                         """, [query]):
        ili[c['id']] = (kind_id[c['kind_id']], c['def'],
                        src_id[c['origin_src_id']], c['src_key'],
                        status_id[c['status_id']], c['superseded_by_id'],
                        c['t'])

    rsumm, up_who, down_who = f_rate_summary(list(ili.keys()))
    return render_template('concept-list.html', ili=ili,
                           rsumm=rsumm, up_who=up_who, down_who=down_who)


@app.route('/upload', methods=['GET', 'POST'])
@login_required(role=0, group='open')
def upload():
    return render_template('upload.html')


@app.route('/join', methods=['GET', 'POST'])
def join():
    return render_template('join.html')

@app.route('/omw/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename, as_attachment=True)


@app.route('/ili/validation-report', methods=['GET', 'POST'])
@login_required(role=0, group='open')
def validationReport():

    vr, filename, wn, wn_dtls = validateFile(current_user.id)

    return render_template('validation-report.html',
                           vr=vr, wn=wn, wn_dtls=wn_dtls,
                           filename=filename)

@app.route('/ili/report', methods=['GET', 'POST'])
@login_required(role=0, group='open')
def report():
    inputfile = request.files.get('file')
    inputurl =  request.form.get('url')
    if inputfile:
        thing, ftype = inputfile, 'webfile'
    elif inputurl:
        thing, ftype = inputfile, 'url'
    else:
        thing, ftype = None, None
    passed, filename = uploadFile(current_user.id, thing, ftype)
    return render_template('report.html',
                           passed=passed,
                           filename=filename)
    # return render_template('report.html')



@app.route('/omw/search', methods=['GET', 'POST'])
@app.route('/omw/search/<lang>/<q>', methods=['GET', 'POST'])
@app.route('/omw/search/<lang>,<lang2>/<q>', methods=['GET', 'POST'])
def search_omw(lang=None, lang2=None, q=None):
    lang_dct, lang_code = fetch_langs()
    if lang and q:
        lang_id = int(lang_code['code'][lang])
        if not lang2:
            lang2 = lang
        lang_id2 = int(lang_code['code'][lang2])
        query = q
    else:
        lang_id = request.form['lang']
        lang_id2 = request.form['lang2']
        query = request.form['query']
        query = query.strip()
        
    sense = od()
    lang_sense = dd(lambda: dd(list))

    if query[0].isalpha(): ### search for inital character of both cases
        if query[0].upper() != query[0].lower():
            query = '['+query[0].upper() + query[0].lower()+']'+query[1:]
    
    # GO FROM FORM TO SENSE, order results by pos
    for s in query_omw("""
        SELECT s.id as s_id, ss_id,  wid, fid, lang_id, pos_id, lemma
        FROM (SELECT w_id as wid, form.id as fid, lang_id, pos_id, lemma
              FROM (SELECT id, lang_id, pos_id, lemma
                    FROM f WHERE lemma GLOB ? AND lang_id in (?,?)) as form
              JOIN wf_link ON form.id = wf_link.f_id) word
        JOIN s ON wid=w_id ORDER BY pos_id
        """, (query, lang_id, lang_id2)):


        sense[s['ss_id']] = [s['s_id'], s['wid'], s['fid'],
                             s['lang_id'], s['pos_id'], s['lemma']]


        lang_sense[s['lang_id']][s['ss_id']] = [s['s_id'], s['wid'], s['fid'],
                                                s['pos_id'], s['lemma']]


    pos = fetch_pos()
  
    ss, senses, defs, exes, links = fetch_ss_basic(sense.keys())
    ili, ili_defs = fetch_ili([ss[k][0] for k in ss])
    labels = fetch_labels(lang_id, set(senses.keys()))

    projects = request.args.get('projects', 'current')
    lang_idm, lang_codem = fetch_langs()
    src_meta = fetch_src_meta()
    src_meta_sorted = fetch_sorted_meta_by_version(projects, src_meta, lang_idm, lang_codem)

    resp = make_response(render_template('omw_results.html',
                                         query =query,
                                         langsel = int(lang_id),
                                         langsel2 = int(lang_id2),
                                         pos = pos,
                                         lang_dct = lang_dct,
                                         sense=sense,
                                         senses=senses,
                                         ss=ss,
                                         ili=ili,
                                         links=links,
                                         defs=defs,
                                         exes=exes,
                                         labels=labels,
                                         src_meta=src_meta_sorted))

    resp.set_cookie('selected_lang', str(lang_id))
    resp.set_cookie('selected_lang2', str(lang_id2))
    return resp

@app.route('/omw/core', methods=['GET', 'POST'])
def omw_core():  ### FIXME add lang as a paramater?
    return render_template('omw_core.html')


@app.route('/omw/concepts/<ssID>', methods=['GET', 'POST'])
@app.route('/omw/concepts/ili/<iliID>', methods=['GET', 'POST'])
def concepts_omw(ssID=None, iliID=None):

    if iliID:
        ss_ids = f_ss_id_by_ili_id(iliID)
        ili, ilidefs = fetch_ili([iliID])
    else:
        ss_ids = [ssID]
        ili, ili_defs = dict(), dict()
    pos = fetch_pos()
    langs_id, langs_code = fetch_langs()
    
    ss, senses, defs, exes, links = fetch_ss_basic(ss_ids)
    if (not iliID) and int(ssID) in ss:
        iliID = ss[int(ssID)][0]
        ili, ilidefs = fetch_ili([iliID])
        
    sss = list(ss.keys())
    for s in links:
        for l in links[s]:
            sss.extend(links[s][l])

    selected_lang = int(_get_cookie('selected_lang', 1))
    selected_lang2 = int(_get_cookie('selected_lang2', 1))
    labels = fetch_labels(selected_lang, set(sss))

    ssrels = fetch_ssrel()

    ss_srcs=fetch_src_for_ss_id(ss_ids)
    src_meta=fetch_src_meta()
    core_ss, core_ili = fetch_core()
    s_ids = []
    for x in senses:
        for y in senses[x]:
            for (s_id, lemma, freq) in senses[x][y]:
                s_ids.append(s_id)
    slinks = fetch_sense_links(s_ids)
    ## get the canonical form for each linked sense
    srl = fetch_srel()
    
    return render_template('omw_concept.html',
                           ssID=ssID,
                           iliID=iliID,
                           pos = pos,
                           langs = langs_id,
                           senses=senses,
                           slinks=slinks,
                           ss=ss,
                           links=links,
                           ssrels=ssrels,
                           defs=defs,
                           exes=exes,
                           ili=ili,
                           selected_lang = selected_lang,
                           selected_lang2 = selected_lang2,
                           labels=labels,
                           ss_srcs=ss_srcs,
                           src_meta=src_meta,
                           core=core_ss,
                           gwadoc=gwadoc,
                           srl=srl)


@app.route('/omw/senses/<sID>', methods=['GET', 'POST'])
def omw_sense(sID=None):
    """display a single sense (and its variants)"""
    if sID:
        langs_id, langs_code = fetch_langs()
        pos = fetch_pos()
        s_id=int(sID)
        sense =  fetch_sense(s_id)
        slinks = fetch_sense_links([s_id])
        forms=fetch_forms(sense[3])
        selected_lang = int(_get_cookie('selected_lang',1))
        labels= fetch_labels(selected_lang,[sense[4]])
        src_meta= fetch_src_meta()
        src_sid=fetch_src_for_s_id([s_id])
        srel = fetch_srel()
        ## get the canonical form for each linked sense
        slabel=fetch_sense_labels([x for v in slinks[int(s_id)].values() for x in v])

        sdefs = fetch_defs_by_sense([s_id])
        sdef = ''
        if selected_lang in sdefs[s_id]:
            sdef = sdefs[s_id][selected_lang] ## requested language
        else:
            sdef = sdefs[min(sdefs[s_id].keys())] ## a language

    return render_template('omw_sense.html',
                           s_id = sID,
                           sdef = sdef,
                           sense = sense,
                           slinks = slinks[s_id],
                           srel = srel,
                           forms=forms,
                           langs = langs_id,
                           pos = pos,
                           labels = labels,
                           slabel = slabel,
                           src_sid = src_sid,
                           src_meta = src_meta,
                           gwadoc=gwadoc)

    
# URIs FOR ORIGINAL CONCEPT KEYS, BY INDIVIDUAL SOURCES
@app.route('/omw/src/<proj>/<ver>/<originalkey>', methods=['GET', 'POST'])
def src_omw(proj=None, ver=None, originalkey=None):

    try:
        src_id = f_src_id_by_proj_ver(proj, ver)
    except:
        src_id = None

    if src_id:
        ss = fetch_ss_id_by_src_orginalkey(src_id, originalkey)
    else:
        ss = None

    return concepts_omw(ss)

##
## show wn statistics
##
##
@app.route('/omw/src/<proj>/<ver>', methods=['GET', 'POST'])
def omw_wn(proj=None,ver=None):
    """
    Present a page describing a single wordnet
    """
    ### default to full = false (short version)
    full = request.args.get('full') in ['true', 'True']
    if proj and ver:
        try:
            src_id = f_src_id_by_proj_ver(proj, ver)
        except:
            src_id = None
        srcs_meta = fetch_src_meta()
        src_info = srcs_meta[src_id]
    if full and src_id: ### give more stats
        ssrel_stats=fetch_ssrel_stats(src_id) 
        srel_stats=fetch_srel_stats(src_id)
    else:
        ssrel_stats= {}
        srel_stats= {}
    pos_stats= fetch_src_id_pos_stats(src_id)
      # get the pos names
    pos = fetch_pos()
    # get the examples for the POS
    pos_ids= [ pos_stats[p]['id'] for p in pos_stats ]
    pos_exe = fetch_pos_id_ss_mf(pos_ids, src_id = src_id)
    ### get the wordnet lang
    langs_id, langs_code = fetch_langs()
    wn_lang = src_info['language']
    wn_lang_id = langs_code['code'][wn_lang]

    # Get the labels for the synsets
    sss = set()
    for p in pos_exe:
        for (ss_id, freq)  in  pos_exe[p]:
            sss.add(ss_id)
    label= fetch_labels(wn_lang_id,sss)

    return render_template('omw_wn.html',
                           proj = proj,
                           ver  = ver,
                           src_id=src_id,
                           src_info=src_info,
                           ssrel_stats=ssrel_stats,
                           srel_stats=srel_stats,
                           pos=pos,
                           pos_stats= pos_stats,
                           pos_exe=pos_exe,
                           label=label,
                           src_stats=fetch_src_id_stats(src_id),
                           licenses=licenses,
                           gwadoc=gwadoc)



@app.route('/omw/src-latex/<proj>/<ver>', methods=['GET', 'POST'])
def omw_wn_latex(proj=None, ver=None,full=False):
    if proj and ver:
        try:
            src_id = f_src_id_by_proj_ver(proj, ver)
        except:
            src_id = None
        srcs_meta = fetch_src_meta()
        src_info = srcs_meta[src_id]
    if full and src_id:
        ssrel_stats=fetch_ssrel_stats(src_id)
    else:
        ssrel_stats= {}

    return render_template('omw_wn_latex.html',
                           proj = proj,
                           ver  = ver,
                           src_id=src_id,
                           src_info=src_info,
                           ssrel_stats=ssrel_stats,
                           pos_stats= fetch_src_id_pos_stats(src_id),
                           src_stats=fetch_src_id_stats(src_id))


@app.route('/cili.tsv')
def generate_cili_tsv():
    tsv = fetch_cili_tsv()
    return Response(tsv, mimetype='text/tab-separated-values')


@app.route('/core.tsv')
def generate_core_tsv():
    """output a list of the core ili concepts
       ToDO: sort by frequency"""
    tsv="""# ili_id\n"""
    core_ss, core_ili = fetch_core()
    for ili in core_ili:
        tsv += "i{}\n".format(ili)
    return Response(tsv, mimetype='text/tab-separated-values')

@app.context_processor
def utility_processor():
    def scale_freq(f, maxfreq=1000):
        if f > 0:
            return 100 + 100 * log(f)/log(maxfreq)
        else:
            return 100
    return dict(scale_freq=scale_freq)

# def style_sense(freq, conf, lang):
#     """show confidence as opacity, show freq as size

#     opacity is the square of the confidence
#     freq is scaled as a % of maxfreq for that language
#     TODO: highlight a word if searched for?"""
#     style = ''
#     if conf and conf < 1.0: ## should not be more than 1.0
#         style += 'opacity: {f};'.format(conf*conf) ## degrade quicker
#     if freq:
#         ### should I be using a log here?
#         maxfreq=1000 #(should do per lang)
#         style += 'font-size: {f}%;'.format(100*(1+ log(freq)/log(maxfreq)))
#     if style:
#         style = "style='{}'".format(style)


###
### WN documentation
###

@app.route('/omw/doc/if', methods=['GET', 'POST'])
def omw_doc_if(name=None):
    return render_template('doc/interface.html')

@app.route('/omw/doc/search', methods=['GET', 'POST'])
def omw_doc_search(name=None):
    return render_template('doc/search.html')

@app.route('/omw/doc/validator', methods=['GET', 'POST'])
def omw_doc_validator(name=None):
    return render_template('doc/validator.html')

@app.route('/omw/doc/feedback', methods=['GET', 'POST'])
def omw_doc_feedback(name=None):
    return render_template('doc/feedback.html')

@app.route('/omw/doc/glob', methods=['GET', 'POST'])
def omw_doc_glob(name=None):
    return render_template('doc/glob.html')

@app.route('/omw/doc/contribute', methods=['GET', 'POST'])
def omw_doc_contribute(name=None):
    return render_template('doc/contribute.html')

@app.route('/omw/doc/feedback-doc', methods=['GET', 'POST'])
def omw_doc_feedback_documentation(name=None):
    return render_template('doc/feedback_documentation.html')

@app.route('/omw/doc/upload', methods=['GET', 'POST'])
def omw_doc_upload(name=None):
    return render_template('doc/upload.html',
                           title="Upload How-To")

@app.route('/omw/doc/metadata', methods=['GET', 'POST'])
def omw_doc_metadata():
    licenses = fetch_licenses()
    return render_template('doc/metadata.html',
                           licenses=licenses)

@app.route('/omw/doc/lmf', methods=['GET', 'POST'])
def omw_doc_lmf():
    return render_template('doc/lmf.html')

@app.route('/omw/doc/', methods=['GET', 'POST'])
@app.route('/omw/doc/wn', methods=['GET', 'POST'])
def omw_doc_wn(name=None):
    return render_template('doc/wn.html',
                           gwadoc=gwadoc)

@app.route('/omw/doc/pos', methods=['GET', 'POST'])
def omw_doc_pos(name=None):
    """
    Provide dynamic documentation for the POS
    ToDo: maybe do per src and or per lang
    """
    ### get the interface language
    selected_lang = int(_get_cookie('selected_lang',1))

    # get the pos names
    pos = fetch_pos()
    # get the examples for the POS
    pos_exe = fetch_pos_id_ss_mf(pos['id'].keys(),
                                 num=5)

    # Get the labels for the synsets
    sss = set()
    for p in pos_exe: 
        for (ss_id, freq)  in  pos_exe[p]:
            sss.add(ss_id)
    label= fetch_labels(selected_lang,sss)
    pos_freq = fetch_pos_id_freq()
    return render_template('doc/pos.html',
                           pos=pos,
                           pos_exe=pos_exe,
                           pos_freq=pos_freq,
                           label=label)


@app.route('/omw/doc/variants', methods=['GET', 'POST'])
def omw_doc_variants(name=None):
    """
    Give some documentation on how variants are represented
    """
    fma =  fetch_form_meta_attr()
    fmv =  fetch_form_meta_val()
    return render_template('doc/variants.html',
                           fma=fma,
                           fmv=fmv)

@app.route('/omw/doc/glossary', methods=['GET', 'POST'])
def omw_doc_glossary(name=None):
    return render_template('doc/glossary.html',
                           gwadoc=gwadoc)

@app.route('/omw/doc/tsv2lmf', methods=['GET', 'POST'])
def omw_doc_tsv2lmf(name=None):
    return render_template('doc/tsv2lmf.html',
                           gwadoc=gwadoc)

@app.route('/omw/doc/add-wn', methods=['GET', 'POST'])
def omw_doc_add_wn(name=None):
    return render_template('doc/add-wn.html',
                           title="Add WN from the Command Line")


@app.route('/omw/doc/doc', methods=['GET', 'POST'])
def omw_doc_doc(name=None):
    return render_template('doc/doc.html',
                           gwadoc=gwadoc)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True)
