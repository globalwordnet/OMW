#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, re, sqlite3, datetime
from flask import Flask, current_app
from flask import render_template, g, request, redirect, url_for, send_from_directory, session, flash
import urllib, gzip, requests
from werkzeug import secure_filename
from lxml import etree

from common_sql import *
from omw_sql import *
from datetime import datetime as dt

import json # to print dd

ILI_DTD = 'db/WN-LMF.dtd'
UPLOAD_FOLDER = 'public-uploads'
ALLOWED_EXTENSIONS = set(['xml','gz','xml.gz'])


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#debug = open ("debug.txt", mode='w')
debug=sys.stderr

with app.app_context():
    good_rels = ['eq_synonym','hypernym','hyponym', 'similar', 'antonym']
    bad_rels = ['also']
    warn_rels = ['agent', 'attribute', 'be_in_state', 'causes',
                 'classified_by', 'classifies', 'co_agent_instrument', 'co_agent_patient',
                 'co_agent_result', 'co_instrument_agent', 'co_instrument_patient',
                 'co_instrument_result', 'co_patient_agent', 'co_patient_instrument',
                 'co_result_agent', 'co_result_instrument', 'co_role', 'direction',
                 'domain_region', 'domain_topic', 'exemplifies', 'entails',
                 'has_domain_region', 'has_domain_topic', 'is_exemplified_by',
                 'holo_location', 'holo_member', 'holo_part', 'holo_portion',
                 'holo_substance', 'holonym', 'in_manner', 'instance_hypernym',
                 'instance_hyponym', 'instrument', 'involved', 'involved_agent',
                 'involved_direction', 'involved_instrument', 'involved_location',
                 'involved_patient', 'involved_result', 'involved_source_direction',
                 'involved_target_direction', 'is_caused_by', 'is_entailed_by',
                 'location', 'manner_of', 'mero_location', 'mero_member', 'mero_part',
                 'mero_portion', 'mero_substance', 'meronym', 'other', 'patient',
                 'restricted_by', 'restricts', 'result', 'role', 'source_direction',
                 'state_of', 'target_direction', 'subevent', 'is_subevent_of']
    ## FCB must be a better way
    ilis=set()

    acceptable_lics = ['wordnet', 
                       'http://opendefinition.org/licenses/cc-by/',
                       'http://opendefinition.org/licenses/cc-by/3.0',
                       'http://opendefinition.org/licenses/cc-by/4.0',
                       'http://opendefinition.org/licenses/odc-by/',
                       'http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html',
                       'http://opendefinition.org/licenses/cc-by-sa/',
                       'http://opendefinition.org/licenses/cc-by-sa/3.0',
                       'http://opendefinition.org/licenses/cc-by-sa/4.0',
                       "https://creativecommons.org/publicdomain/zero/1.0/",
                       "https://creativecommons.org/licenses/by/",
                       "https://creativecommons.org/licenses/by-sa/",
                       "https://creativecommons.org/licenses/by/3.0/",
                       "https://creativecommons.org/licenses/by-sa/3.0/",
                       "https://creativecommons.org/licenses/by/4.0/",
                       "https://creativecommons.org/licenses/by-sa/4.0/",
                       "http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html",
                       'https://opensource.org/licenses/MIT/',
                       'https://opensource.org/licenses/Apache-2.0']
    mindefchars=20
    mindefwords=4
    
    
    def parse_wn(wnlmf):

        ### LOG     
        #print('Starting to parse data\t{}'.format(dt.today().isoformat()))   
        langs, langs_code = fetch_langs()
        ili, ili_defs = fetch_ili()

        l=lambda:dd(l)
        wn_dtls = l()
        synset_senses = l()
        wn = l()

        ########################################################################
        # LEXICONS (1st ITERATION: LEXICAL ENTRIES)
        ########################################################################
        for lexi in wnlmf.findall('Lexicon'):
            lexicon = lexi.get('id')
            lexicon_attrs = lexi.attrib
            wn[lexicon]['attrs'] = lexicon_attrs
            lexi_lang = wn[lexicon]['attrs']['language']
            try:
                lexi_lang = langs_code['code'][lexi_lang]
            except:
                pass
            ### LOG
            # print("Reading Lexicon {} for Language {} ({})\t{}".format(lexicon,
            #                                                            lexi_lang,
            #                                                            lexicon_attrs,
            #                                                            dt.today().isoformat()))
            ####################################################################
            # LEXICAL ENTRIES (CAN LINK OVER MULTIPLE LEXICONS)
            ####################################################################
            wn_dtls['bad_sensExe_lang'][lexicon] = []
            for lex_ent in lexi.findall('LexicalEntry'):
                le_id = lex_ent.get('id')
                le = wn[lexicon]['le'][le_id]
                le['attrs'] = lex_ent.attrib

                # LEXICAL ENTRY LEMMA
                lem = lex_ent.find('Lemma')
                le['lemma']['attrs'] = lem.attrib

                le['lemma']['tags'] = []
                for lem_tag in lem.findall('Tag'):
                    lem_tag_lbl = lem_tag.get('category')
                    lem_tag_val = lem_tag.text
                    le['lemma']['tags'].append((lem_tag_lbl, lem_tag_val))

                # LEXICAL ENTRY FORMS
                for lem_form in lex_ent.findall('Form'):
                    lem_form_w = lem_form.get('writtenForm')

                    if 'script' in lem_form.attrib.keys():
                        lem_form_script = lem_form.get('script')
                    else:
                        lem_form_script = None

                    lemform = le['forms'][(lem_form_w, lem_form_script)]
                    lemform['tags'] = []
                    for lem_form_tag in lem_form.findall('Tag'):
                        lem_form_tag_lbl = lem_form_tag.get('category')
                        lem_form_tag_val = lem_form_tag.text
                        lemform['tags'].append((lem_form_tag_lbl,
                                                lem_form_tag_val))


                # LEXICAL ENTRY SENSES
                for sense in lex_ent.findall('Sense'):
                    sens_id = sense.attrib['id']
                    sens_synset = sense.attrib['synset']

                    # ADD SENSES IN A NON LEXICON DEPENDENT FORMAT
                    synset_senses[sens_synset][(lexicon,le_id)] = lem.attrib['partOfSpeech']

                    wn_sens = le['senses'][(sens_id, sens_synset)]
                    wn_sens['attrs'] = sense.attrib

                    for sensRel in sense.findall('SenseRelation'):
                        sensTrgt = sensRel.get('Target')
                        relType = sensRel.get('relType')

                        wn_sensRels = wn_sens['rels'][(relType, sensTrgt)]
                        wn_sensRels['attrs'] = sensRel.attrib

                    for sensExes in sense.findall('Example'):
                        sensExes_txt = sensExes.text
                        try:
                            sensExes_lang = sensExes.attrib['language']
                            try:
                                sensExes_lang = langs_code['code'][sensExes_lang]
                                if sensExes_lang == lexi_lang:
                                    pass
                                else: # rejects because the language is bad
                                    wn_dtls['bad_sensExe_lang'][lexicon].append((sens_id,sensExes_txt))
                            except:  # rejects because the language doesn't exist
                                wn_dtls['bad_sensExe_lang'][lexicon].append((sens_id,sensExes_txt))
                        except:
                            sensExes_lang = lexi_lang # inherits from lexicon

                        wn_sensExes = wn_sens['exes'][(sensExes_lang,
                                                       sensExes_txt)]
                        wn_sensExes['attrs'] = sensExes.attrib


                    for i, sensCount in enumerate(sense.findall('Count')):
                        sensCount_txt = sensCount.text

                        wn_sensExes = wn_sens['counts'][(i,sensCount_txt)]
                        wn_sensExes['attrs'] = sensCount.attrib


                # LEXICAL ENTRY SYNTACTIC BEHAVIOUR
                le['subcat'] = []
                for synBehav in lex_ent.findall('SyntacticBehaviour'):
                    subcat = synBehav.get('subcategorizationFrame')
                    le['subcat'].append(subcat)
            ####################################################################


        ### LOG     
        # print('Lexemes and senses read for {}\t{}'.format(lexicon,
        #                                                 dt.today().isoformat()))
        
        ########################################################################
        # LEXICONS (2n ITTERATION: SYNSETS)
        ########################################################################
        for lexi in wnlmf.findall('Lexicon'):
            lexicon = lexi.get('id')
            lexicon_attrs = lexi.attrib
            wn[lexicon]['attrs'] = lexicon_attrs
            lexi_lang = wn[lexicon]['attrs']['language']
            try:
                lexi_lang = langs_code['code'][lexi_lang]
            except:
                pass

            ####################################################################
            # SYNSETS
            ####################################################################
            wn_dtls['bad_ss_id'][lexicon]=list()  # check synset.id format
            wn_dtls['bad_ss_pos'][lexicon]=list()  # check synset pos from lemmas
            wn_dtls['bad_ss_ili'][lexicon]=list() # check synset.ili format/existance
            wn_dtls['bad_ss_def_lang'][lexicon]=list() # check synset.definition.lang
            wn_dtls['bad_ss_def_empty'][lexicon]=list() # check synset.definition.text
            wn_dtls['bad_ss_ex_lang'][lexicon]=list() # check synset.example.lang
            wn_dtls['bad_ss_ex_empty'][lexicon]=list() # check synset.definition.text
            wn_dtls['ss_ili_new'][lexicon]=list() # list of newly proposed ILI synsets
            wn_dtls['ss_ili_out'][lexicon]=list() # list of synsets unlinked from ILI
            wn_dtls['ss_ili_linked'][lexicon]=list() # list of synsets with ILI id

            for ss in lexi.findall('Synset'):

                ss_id = ss.get('id')
                ss_attrs = ss.attrib
                synset = wn[lexicon]['syns'][ss_id]
                synset['attrs'] = ss_attrs



                # Check Synset id naming convention
                if not ss_attrs['id'].startswith(lexicon_attrs['id']+'-'):
                    wn_dtls['bad_ss_id'][lexicon].append(ss_id)
                else:
                    strip = len(lexicon_attrs['id'])+1
                    synset['ili_origin_key'] = ss_id[strip:]


                syn_pos = set()  # THERE CAN BE ONLY ONE POS!

                # ADD THE POS OF THE SYNSET
                if 'partOfSpeech' in synset['attrs'].keys():
                    syn_pos.add(synset['attrs']['partOfSpeech'])

                # ADD THE POS OF EACH SENSE
                for lexicon, le_id in synset_senses[ss_id].keys():
                    syn_pos.add(synset_senses[ss_id][(lexicon,le_id)])

                if len(syn_pos) != 1: # we have a pos problem
                    syn_pos = ', '.join(str(p) for p in syn_pos)
                    syn_pos = None if syn_pos == '' else syn_pos
                    wn_dtls['bad_ss_pos'][lexicon].append((ss_id, syn_pos))
                else:
                    wn[lexicon]['syns'][ss_id]['SSPOS'] = list(syn_pos)[0]

                # Check ILI attribute compliance
                ili_pattern = "^[i][0-9]+$"
                if ss_attrs['ili'] == "": # Not linked to ILI
                    wn_dtls['ss_ili_out'][lexicon].append(ss_id)
                    synset['ili_key'] = None

                elif ss_attrs['ili'] == "in": # New ILI candidate
                    wn_dtls['ss_ili_new'][lexicon].append(ss_id)
                    synset['ili_key'] = None

                elif re.search(ili_pattern, ss_attrs['ili']):
                    ili_id = int(ss.get('ili')[1:])

                    if ili_id in ili:
                        wn_dtls['ss_ili_linked'][lexicon].append(ss_id)
                        synset['ili_key'] = ili_id
                        ilis.add(ss_id)   ### FCB
                    else:
                        wn_dtls['bad_ss_ili'][lexicon].append(ss_id)
                        synset['ili_key'] = False

                else: # some other weird ili value was found
                    wn_dtls['bad_ss_ili'][lexicon].append(ss_id)
                    synset['ili_key'] = False


                # SYNSET ILI DEFINITION (OPTIONAL, 0 or 1)
                ili_def = ss.find('ILIDefinition')
                if ili_def is not None:
                    ili_def_lang = langs_code['code']['en']
                    synset['ili_def'][(ili_def_lang,ili_def.text)]['attrs'] = ili_def.attrib


                # SYNSET DEFINITIONS (OPTIONAL, 0 or more)
                for definition in ss.findall('Definition'):

                    def_txt = definition.text
                    def_attrs = definition.attrib

                    try:
                        def_lang = langs_code['code'][def_attrs['language']]
                        if def_lang:
                            pass
                        else: # Must reject this synset because the language is bad
                            wn_dtls['bad_ss_def_lang'][lexicon].append(ss_id)
                    except:
                        def_lang = lexi_lang # inherits from lexicon language

                    if def_txt:
                        pass
                    else:
                        wn_dtls['bad_ss_def_empty'][lexicon].append(ss_id)


                    synset['def'][(def_lang,def_txt)]['attrs'] = def_attrs



                # SYNSET EXAMPLES (OPTIONAL, 0 or more)
                for example in ss.findall('Example'):

                    example_txt = example.text
                    example_attrs = example.attrib

                    try:

                        example_lang = langs_code['code'][example_attrs['language']]
                        if example_lang:
                            pass
                        else: # Must reject this synset because the language is bad
                            wn_dtls['bad_ss_ex_lang'][lexicon].append(ss_id)
                    except:
                        example_lang = lexi_lang # inherits from lexicon language

                    if example_txt:
                        pass
                    else:
                        wn_dtls['bad_ss_ex_empty'][lexicon].append(ss_id)

                    synset['ex'][(example_lang,example_txt)]['attrs'] = example_attrs



                # SYNSET RELATIONS
                # FIXME: CHECK IF THE TARGET_ID TO LINK EXISTS (?)
                for ss_r in ss.findall('SynsetRelation'): # Multiple rels per ss

                    ss_r_attrs = ss_r.attrib
                    ss_r_type = ss_r_attrs['relType']
                    ss_r_target = ss_r_attrs['target']

                    synset['ssrel'][(ss_r_type,ss_r_target)]['attrs'] = ss_r_attrs


                    # ILI CONCEPT KIND (CONCEPT vs INSTANCE)
                    if ss_r_type == "instance_hypernym":
                        synset['ili_kind'] = 2
                        synset['ili_kind_str'] = 'instance'
                    else:
                        synset['ili_kind'] = 1
                        synset['ili_kind_str'] = 'concept'
        ### LOG     
        # print('Synsets read for {}\t{}'.format(lexicon,
        #                                        dt.today().isoformat()))


        return wn, wn_dtls




    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


    def uploadFile(current_user):

        format = "%Y_%b_%d_%H:%M:%S"
        now = datetime.datetime.utcnow().strftime(format)

        try:
            file = request.files['file']
        except:
            file = None
        try:
            url = request.form['url']
        except:
            url = None

        if file and allowed_file(file.filename):
            filename = now + '_' +str(current_user) + '_' + file.filename
            filename = secure_filename(filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_uploaded = True

        elif url:
            file = urllib.urlopen(url)
            filename = url.split('/')[-1]
            filename = now + '_' +str(current_user) + '_' + filename
            filename = secure_filename(filename)

            if file and allowed_file(filename):

                open(os.path.join(app.config['UPLOAD_FOLDER'], filename),
                     'wb').write(file.read())
            file_uploaded = True

        else:
            filename = None
            file_uploaded = False

        return file_uploaded, filename

    def val1_DTD(current_user, filename):  # MATCH WN AGAINST DTD

        l=lambda:dd(l)
        vr = l()  # validation report

        dtd_f = open(ILI_DTD, 'rb')
        try:
            dtd = etree.DTD(dtd_f)

            if filename.endswith('.xml'):
                wn = open(os.path.join(app.config['UPLOAD_FOLDER'],
                                       filename), 'rb')
                wnlmf = etree.XML(wn.read())
                vr['lmf_dump'] = wn.read()

            elif filename.endswith('.gz'):
                with gzip.open(os.path.join(app.config['UPLOAD_FOLDER'],
                                            filename), 'rb') as wn:
                    wnlmf = etree.XML(wn.read())
                    vr['lmf_dump'] = wn.read()


            vr['read'] = True
            if dtd.validate(wnlmf):
                vr['dtd_val'] = True
            else:
                vr['dtd_val'] = False
                vr['dtd_val_errors'] = str(dtd.error_log.filter_from_errors()[0])

        except:
            vr['read'] = False
            vr['dtd_val'] = False
            vr['final_validation'] = False

        dtd_f.close()
        return vr


    def val2_metadata(vr_master):
        l=lambda:dd(l)
        vr = l()  # validation report
        vr.update(vr_master)

        wnlmf = etree.XML(vr['lmf_dump'])
        # if vr['dtd_val']:

        # if filename and filename.endswith('.xml'):
        #     wn = open(os.path.join(app.config['UPLOAD_FOLDER'],
        #                                filename), 'rb')
        #     wnlmf = etree.XML(wn.read())

        # elif filename and filename.endswith('.gz'):
        #     with gzip.open(os.path.join(app.config['UPLOAD_FOLDER'],
        #                                     filename), 'rb') as wn:
        #         wnlmf = etree.XML(wn.read())

        if wnlmf is not None and vr['dtd_val']:

            wn, wn_dtls = parse_wn(wnlmf)
            projs = fetch_proj()
            langs, langs_code = fetch_langs()

            vr['num_lexicons_found'] = len(wn.keys())
            vr['lexicons_found'] = list(wn.keys())


            invalid_ililinks = set() # TO CHECK ILI LINK COMFORMITY
            for lexicon in wn:
                vr_lex = vr['lexicon'][lexicon]

                ################################################################
                # CHECK META-DATA
                ################################################################
                lexicon_lbl = wn[lexicon]['attrs']['id']
                lexicon_id =  f_proj_id_by_code(lexicon_lbl)
                vr_lex['lex_lbl_val'] = lexicon_lbl
                if wn[lexicon]['attrs']['id'] in projs.values():
                    vr_lex['lex_lbl'] = True
                else:
                    vr_lex['lex_lbl'] = False
                    final_validation = False

                lang_lbl = wn[lexicon]['attrs']['language']
                try:
                    lang_id = langs_code['code'][lang_lbl]
                except:
                    lang_id = None
                vr_lex['lang_lbl_val'] = lang_lbl
                if lang_id in langs.keys():
                    vr_lex['lang_lbl'] = True
                else:
                    vr_lex['lang_lbl'] = False
                    final_validation = False

                version = wn[lexicon]['attrs']['version']
                vr_lex['version_lbl_val'] = version
                if f_src_id_by_proj_ver(lexicon_id, version):
                    vr_lex['version_lbl'] = False
                    final_validation = False
                else:
                    vr_lex['version_lbl'] = True


                if 'confidenceScore' in wn[lexicon]['attrs'].keys():
                    confidence = wn[lexicon]['attrs']['confidenceScore']
                    vr_lex['confidence_lbl_val'] = confidence
                else:
                    confidence = None
                    vr_lex['confidence_lbl_val'] = str(confidence)
                try:
                    if float(confidence) == 1.0:
                        vr_lex['confidence_lbl'] = True
                    else:
                        vr_lex['confidence_lbl'] = 'warning'
                except:
                        vr_lex['confidence_lbl'] = False
                        final_validation = False


                lic = wn[lexicon]['attrs']['license']
                vr_lex['license_lbl_val'] = lic
                if lic in acceptable_lics:
                    vr_lex['license_lbl'] = True
                else:
                    vr_lex['license_lbl'] = False
                    final_validation = False
                ################################################################
        return vr



        
    # def load_all_rels(wn, unlinked, starting_rels, list_of_rels, i):
    #     """
    #     This takes in a dictionary of synsets and populates it with
    #     a set of relations each synset is involved with, taking the
    #     whole wordnet.
    #     It produces a dictionary of synsets and a set of synsets
    #     that it links to, using a given list of relations.
    #     """
    #     all_rels = dd(set)
    #     for key, item in starting_rels.items():
    #         all_rels[key] = item

    #     for c in list(all_rels.keys()):
    #         for (typ, trgt) in wn['syns'][c]['ssrel']:

    #             # filter by rels & excluding synsets not linked to ILI
    #             if typ in list_of_rels and \
    #                c not in unlinked and \
    #                trgt not in unlinked:

    #                 all_rels[c].add(trgt)
    #                 all_rels[trgt].add(c)

    #     # expand relations (add links of links)
    #     for concept in list(all_rels.keys()):
    #         for target in all_rels[concept]:
    #             all_rels[concept] = all_rels[concept] | all_rels[target]

    #     if starting_rels == all_rels: # being exaustive, not limiting i
    #         return all_rels
    #     else:
    #         ###LOG
    #         print ("Checking one level deeper: {}\t{}".format(i+1,dt.today().isoformat()))
    #         return load_all_rels(wn, unlinked, all_rels, list_of_rels, i+1)


    def checkLinked(lnks, rels, ilis, ss, visited):
        """take a dict of links: lnks[src][lnk][trg] = conf
        a set of ok relations (rels)
        a list of synsets linked to ili: ilis = set()
        check if a new synset (ss) is linked up
        visited is a list of synsets that have been checked (and found wanting)
        if a linked synset is found, return True and stop
        """
        if not visited:
            visited.add(ss) 
        for lnk in lnks[ss]:
            if lnk in rels:
                for trg in set(lnks[ss][lnk].keys()) - visited: ### confidence?
                    if trg in ilis:
                        #print('CHECKED:', ss, lnk, trg, file=debug)  ##DEBUG
                        return True
                    else:
                        #print('CHECKING:', ss, lnk, trg, file=debug)  ##DEBUG
                        visited.add(trg)
                        return checkLinked(lnks,rels,ilis,trg,visited)
        ## if we run out of things to visit then it is not linked
        return False
                        


    def validateFile(current_user, filename):

        l=lambda:dd(l)
        vr = l()  # validation report
        final_validation = True # assume it will pass

        vr['upload'] = True
        
        ###LOG
        print('Preparing to Validate File\t{}'.format(dt.today().isoformat()))
        ########################################################################
        # FETCH & UPLOAD WN FILE/URL
        ########################################################################
        # if request.method == 'POST':
        #     format = "%Y_%b_%d_%H:%M:%S"
        #     now = datetime.datetime.utcnow().strftime(format)

        #     try:
        #         file = request.files['file']
        #     except:
        #         file = None
        #     try:
        #         url = request.form['url']
        #     except:
        #         url = None

        #     if file and allowed_file(file.filename):
        #         filename = now + '_' +str(current_user) + '_' + file.filename
        #         filename = secure_filename(filename)
        #         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        #     elif url:
        #         file = urllib.urlopen(url)
        #         filename = url.split('/')[-1]
        #         filename = now + '_' +str(current_user) + '_' + filename
        #         filename = secure_filename(fn)  ### FIXME

        #         if file and allowed_file(filename):

        #             open(os.path.join(app.config['UPLOAD_FOLDER'], filename),
        #                  'wb').write(file.read())


        #     vr['upload'] = True
        # ###LOG
        # print('Uploaded file {}\t{}'.format('file', dt.today().isoformat()))
 
        ########################################################################
        # CHECK WN STRUCTURE (MATCH AGAINST DTD)
        ########################################################################
        dtd_f = open(ILI_DTD, 'rb')

        try:
            dtd = etree.DTD(dtd_f)

            if filename.endswith('.xml'):

                wn = open(os.path.join(app.config['UPLOAD_FOLDER'],
                                       filename), 'rb')
                wnlmf = etree.XML(wn.read())


            elif filename.endswith('.gz'):
                with gzip.open(os.path.join(app.config['UPLOAD_FOLDER'],
                                            filename), 'rb') as wn:
                    wnlmf = etree.XML(wn.read())

            vr['read'] = True


            if dtd.validate(wnlmf):
                vr['dtd_val'] = True

            else:
                vr['dtd_val'] = False
                vr['dtd_val_errors'] = str(dtd.error_log.filter_from_errors()[0])
                final_validation = False

                wnlmf = None
                filename = None

        except:
            wnlmf = None
            filename = None


            vr['read'] = False
            vr['dtd_val'] = False
            final_validation = False


        dtd_f.close()
        ###LOG
        # print('Validated DTD {} ({})\t{}'.format(final_validation, filename,
        #       dt.today().isoformat()))


        ########################################################################
        # CHECK WN DATA INTEGRITY
        ########################################################################
        ### why do we validate again?  haven't we done that? CHECKME (save 8s!)
        
        if final_validation: #wnlmf is not None and dtd.validate(wnlmf):

            wn, wn_dtls = parse_wn(wnlmf)
            projs = fetch_proj()
            langs, langs_code = fetch_langs()

            vr['num_lexicons_found'] = len(wn.keys())
            vr['lexicons_found'] = list(wn.keys())


            invalid_ililinks = set() # TO CHECK ILI LINK COMFORMITY
            for lexicon in wn:
                ### LOG     
                # print('Checking {}\t{}'.format(lexicon,
                #                                dt.today().isoformat()))

                vr_lex = vr['lexicon'][lexicon]

                ################################################################
                # CHECK META-DATA
                ################################################################
                lexicon_lbl = wn[lexicon]['attrs']['id']
                lexicon_id =  f_proj_id_by_code(lexicon_lbl)
                vr_lex['lex_lbl_val'] = lexicon_lbl
                if wn[lexicon]['attrs']['id'] in projs.values():
                    vr_lex['lex_lbl'] = True
                else:
                    vr_lex['lex_lbl'] = False
                    final_validation = False

                lang_lbl = wn[lexicon]['attrs']['language']
                try:
                    lang_id = langs_code['code'][lang_lbl]
                except:
                    lang_id = None
                vr_lex['lang_lbl_val'] = lang_lbl
                if lang_id in langs.keys():
                    vr_lex['lang_lbl'] = True
                else:
                    vr_lex['lang_lbl'] = False
                    final_validation = False

                version = wn[lexicon]['attrs']['version']
                vr_lex['version_lbl_val'] = version
                if f_src_id_by_proj_id_ver(lexicon_id, version):
                    vr_lex['version_lbl'] = False
                    final_validation = False
                else:
                    vr_lex['version_lbl'] = True


                if 'confidenceScore' in wn[lexicon]['attrs'].keys():
                    confidence = wn[lexicon]['attrs']['confidenceScore']
                    vr_lex['confidence_lbl_val'] = confidence
                else:
                    confidence = None
                    vr_lex['confidence_lbl_val'] = str(confidence)
                try:
                    if float(confidence) == 1.0:
                        vr_lex['confidence_lbl'] = True
                    else:
                        vr_lex['confidence_lbl'] = 'warning'
                except:
                        vr_lex['confidence_lbl'] = False
                        final_validation = False


                lic = wn[lexicon]['attrs']['license']
                vr_lex['license_lbl_val'] = lic
                if lic in acceptable_lics:
                    vr_lex['license_lbl'] = True
                else:
                    vr_lex['license_lbl'] = False
                    final_validation = False
                ################################################################
                ### LOG     
                # if final_validation:
                #     print('Meta Data OK for {}\t{}'.format(lexicon,
                #                                            dt.today().isoformat()))
        
                ################################################################
                # CHECK ALL CONCEPTS
                ################################################################
                # TOTAL CONCEPTS
                syns_total = len(wn[lexicon]['syns'].keys())
                vr_lex['synsets_lbl_val'] = syns_total
                if syns_total > 0:
                    vr_lex['synsets_lbl'] = True
                else:
                    vr_lex['synsets_lbl'] = 'warning'

                # SYNSETS W/ BAD ID (CONVENTION lexicon_id-origin_synset_id)
                syns_bad_id_total = len(wn_dtls['bad_ss_id'][lexicon])
                vr_lex['synsets_bad_id_lbl_val'] = wn_dtls['bad_ss_id'][lexicon]
                if syns_bad_id_total > 0:
                    vr_lex['synsets_bad_id_lbl'] = False
                    final_validation = False
                else:
                    vr_lex['synsets_bad_id_lbl'] = True


                # SYNSETS W/ BAD POS (BY LEMMAS)
                vr_lex['synsets_bad_pos_val'] = wn_dtls['bad_ss_pos'][lexicon]
                if len(wn_dtls['bad_ss_pos'][lexicon]) > 0:
                    vr_lex['synsets_bad_pos_lbl'] = False
                    final_validation = False
                else:
                    vr_lex['synsets_bad_pos_lbl'] = True


                # SYNSETS W/ BAD SENSE-EXAMPLE LANGUAGES
                bad_sensExe_lang = wn_dtls['bad_sensExe_lang'][lexicon]
                vr_lex['synsets_bad_sensExe_lang_val'] = bad_sensExe_lang
                if len(bad_sensExe_lang) > 0:
                    vr_lex['synsets_bad_sensExe_lang_lbl'] = False
                    final_validation = False
                else:
                    vr_lex['synsets_bad_sensExe_lang_lbl'] = True

                # SYNSETS WITH ILI KEYS
                syns_with_ili_total = len(wn_dtls['ss_ili_linked'][lexicon])
                vr_lex['synsets_with_ili_lbl_val'] = syns_with_ili_total
                if syns_with_ili_total > 0:
                    vr_lex['synsets_with_ili_lbl'] = True
                else:
                    vr_lex['synsets_with_ili_lbl'] = 'warning'

                # SYNSETS W/ BAD ILI KEYS (bad or inexistent)
                syns_bad_ili_total = len(wn_dtls['bad_ss_ili'][lexicon])
                vr_lex['synsets_bad_ili_lbl_val'] = wn_dtls['bad_ss_ili'][lexicon]
                if syns_bad_ili_total > 0:
                    vr_lex['synsets_bad_ili_lbl'] = False
                    final_validation = False
                else:
                    vr_lex['synsets_bad_ili_lbl'] = True

                # SYNSETS W/ BAD DEF LANG CODES
                syns_bad_ili_total = len(wn_dtls['bad_ss_def_lang'][lexicon])
                vr_lex['synsets_ss_def_lang_lbl_val'] = wn_dtls['bad_ss_def_lang'][lexicon]
                if syns_bad_ili_total > 0:
                    vr_lex['synsets_ss_def_lang_lbl'] = False
                    final_validation = False
                else:
                    vr_lex['synsets_ss_def_lang_lbl'] = True

                # SYNSETS W/ BAD (EMPTY) DEF
                syns_bad_ili_total = len(wn_dtls['bad_ss_def_empty'][lexicon])
                vr_lex['synsets_ss_def_empty_lbl_val'] = wn_dtls['bad_ss_def_empty'][lexicon]
                if syns_bad_ili_total > 0:
                    vr_lex['synsets_ss_def_empty_lbl'] = False
                    final_validation = False
                else:
                    vr_lex['synsets_ss_def_emtpy_lbl'] = True


                # SYNSETS W/ BAD EXAMPLE LANG CODES
                syns_bad_ili_total = len(wn_dtls['bad_ss_ex_lang'][lexicon])
                vr_lex['synsets_ss_ex_lang_lbl_val'] = wn_dtls['bad_ss_ex_lang'][lexicon]
                if syns_bad_ili_total > 0:
                    vr_lex['synsets_ss_ex_lang_lbl'] = False
                    final_validation = False
                else:
                    vr_lex['synsets_ss_ex_lang_lbl'] = True

                # SYNSETS W/ BAD (EMPTY) EXAMPLE
                syns_bad_ili_total = len(wn_dtls['bad_ss_ex_empty'][lexicon])
                vr_lex['synsets_ss_ex_empty_lbl_val'] = wn_dtls['bad_ss_ex_empty'][lexicon]
                if syns_bad_ili_total > 0:
                    vr_lex['synsets_ss_ex_empty_lbl'] = False
                    final_validation = False
                else:
                    vr_lex['synsets_ss_ex_emtpy_lbl'] = True



                # SYNSETS WITHOUT ILI KEY OR 'IN' STATUS
                syns_ili_out_total = len(wn_dtls['ss_ili_out'][lexicon])
                vr_lex['synsets_ili_out_lbl_val'] = syns_ili_out_total
                if syns_ili_out_total == 0:
                    vr_lex['synsets_ili_out_lbl'] = True
                else:
                    vr_lex['synsets_ili_out_lbl'] = 'warning'

                # NEW ILI CANDIDATES
                syns_ili_new_total = len(wn_dtls['ss_ili_new'][lexicon])
                vr_lex['synsets_ili_new_lbl_val'] = syns_ili_new_total
                if syns_ili_new_total > 0:
                    vr_lex['synsets_ili_new_lbl'] = True
                else:
                    vr_lex['synsets_ili_new_lbl'] = 'warning'
                ################################################################
                ### LOG     
                # if final_validation:
                #     print('Synsets well formed {}\t{}'.format(lexicon,
                #                                               dt.today().isoformat()))
                #     print("Let's check the new candidates, ...")

                ################################################################
                # CHECK NEW ILI CANDIDATES
                ################################################################
                ili, ili_defs = fetch_ili()
                new_ili_defs = dict()

                vr_lex['synsets_ili_def_notexists_lbl'] = True
                vr_lex['synsets_ili_def_notexists_lbl_val'] = []

                vr_lex['ili_def_conf_lbl'] = True
                vr_lex['ili_def_conf_lbl_val'] = []
                vr_lex['synsets_ili_def_length_lbl'] = True
                vr_lex['synsets_ili_def_length_lbl_val'] = []
                vr_lex['synsets_ili_def_nonuniq_lbl'] = True
                vr_lex['synsets_ili_def_nonuniq_lbl_val'] = []
                vr_lex['synsets_ili_def_nonuniq2_lbl'] = True
                vr_lex['synsets_ili_def_nonuniq2_lbl_val'] = []


                new_wn_rels = dd(set)
                vr_lex['synsets_ili_lnk_none'] = []  # not linked
                vr_lex['synsets_ili_lnk_bad'] = []  # linked only by bad 
                vr_lex['synsets_ili_lnk_warn'] = [] # linked only by weak






                ###new_ili_ss = dict((ss_id, set()) for ss_id in wn_dtls['ss_ili_new'][lexicon])
                #all_rels_good = load_all_rels(wn[lexicon],wn_dtls['ss_ili_out'][lexicon],
                #                              new_ili_ss, good_rels, 0)
                #all_rels_warn = load_all_rels(wn[lexicon],wn_dtls['ss_ili_out'][lexicon],
                #
                #new_ili_ss, good_rels+warn_rels, 0)
                ###  dict of links: lnks[src][lnk][trg] = conf
                lnks = dd(lambda: dd(lambda: dd(float)))
                for s in wn[lexicon]['syns']:
                    for  (typ, trg) in wn[lexicon]['syns'][s]['ssrel']:
                        lnks[s][typ][trg] = 1.0
                ###
                ### this only gets ilis from this resource!
                ### should do better
                ###
                #ilis = set(wn[lex]['syns'][target]['ili_key'] for i in ili.keys())
                ### DEBUG
                #print ('LNKS: ' + json.dumps(lnks, indent=2), file=debug)
                #print ('ILIS: ' + ", ".join(str(i) for i in ilis), file=debug)
                ###LOG
                # print('Loaded all rels {}\t{}'.format(lexicon,
                #                                       dt.today().isoformat()))
                for ss_id in wn_dtls['ss_ili_new'][lexicon]:
                    synset = wn[lexicon]['syns'][ss_id]

                    # CHECK IF ILI DEFINITION EXISTS
                    if not synset['ili_def']:
                        vr_lex['synsets_ili_def_notexists_lbl_val'].append(ss_id)
                        vr_lex['synsets_ili_def_notexists_lbl'] = False
                        final_validation = False

                    # CHECK ILI DEFINITIONS
                    for (ili_def_lang, ili_def) in synset['ili_def'].keys():

                        # CHECK ILI DEFINITION CONFIDENCESCORE
                        ili_def_attrs = synset['ili_def'][(ili_def_lang, ili_def)]['attrs']
                        if 'confidenceScore' in ili_def_attrs.keys():
                            ili_def_conf = wn[lexicon]['attrs']['confidenceScore']
                        elif 'confidenceScore' in synset['attrs'].keys():
                            ili_def_conf = synset['attrs']['confidenceScore']
                        else:
                            ili_def_conf = vr_lex['confidence_lbl_val']
                        try:
                            if float(ili_def_conf) != 1.0:
                                vr_lex['ili_def_conf_lbl_val'].append((ss_id,ili_def_conf))
                                vr_lex['ili_def_conf_lbl'] = False
                                final_validation = False
                        except:
                            vr_lex['ili_def_conf_lbl_val'].append((ss_id,ili_def_conf))
                            vr_lex['ili_def_conf_lbl'] = False
                            final_validation = False

                        # CHECK ILI DEFINITIONS' LENGTH
                        if not (ili_def or len(ili_def) < mindefchars or \
                           len(ili_def.split()) < mindefwords):
                            vr_lex['synsets_ili_def_length_lbl_val'].append((ss_id,ili_def))
                            vr_lex['synsets_ili_def_length_lbl'] = False
                            final_validation = False

                        # CHECK ILI DEFINITIONS' NON UNIQUE WITH PREVIOUS DEFS
                        elif ili_def in ili_defs:
                            val = ('ili'+str(ili_defs[ili_def]), ss_id, ili_def)
                            vr_lex['synsets_ili_def_nonuniq_lbl_val'].append(val)
                            vr_lex['synsets_ili_def_nonuniq_lbl'] = False
                            final_validation = False

                        # CHECK ILI DEFINITIONS' NON UNIQUE WITHIN PROPOSED ILI DEFS
                        elif ili_def in new_ili_defs:
                            val = (new_ili_defs[ili_def], ss_id, ili_def)
                            vr_lex['synsets_ili_def_nonuniq2_lbl_val'].append(val)
                            vr_lex['synsets_ili_def_nonuniq2_lbl'] = False
                            final_validation = False

                        else:
                            new_ili_defs[ili_def] = ss_id

                    ### check for closeness!    
                    ### LOG
                    # print('ILI def checked {}: {} {}\t{}'.format(lexicon, ss_id,
                    #                                              final_validation,
                    #                                              dt.today().isoformat()))


                    ########################################################
                    # RELATIONS
                    ########################################################
                    # FIXME! CHECK LINKS' CONFIDENCE = 1.0 (?)

                    link_to_ili = 'None'
                    if checkLinked(lnks, good_rels, ilis, ss_id, set()):
                        link_to_ili = 'good'
                        #print("LINKED g:",  link_to_ili, ss_id, file=debug)
                    elif checkLinked(lnks, good_rels+warn_rels, ilis, ss_id, set()):
                        link_to_ili = 'weak'
                        vr_lex['synsets_ili_lnk_warn'].append(ss_id)
                        #print("LINKED w:",  link_to_ili, ss_id, file=debug)
                    elif checkLinked(lnks, good_rels+warn_rels+bad_rels,
                                     ilis, ss_id, set()):
                        link_to_ili = 'bad'
                        vr_lex['synsets_ili_lnk_bad'].append(ss_id)
                        final_validation = False
                        #print("LINKED b:",  link_to_ili, ss_id, file=debug)
                    else:
                        vr_lex['synsets_ili_lnk_none'].append(ss_id)
                        final_validation = False
                        #print("LINKED n:",  link_to_ili, ss_id, file=debug)
                    # print("LINK:",  link_to_ili, ss_id, file=debug)

                    #print("VALID:",  ss_id, final_validation, file=debug)
                    # Synsets don't need to be in the same lexicon
                    # for target in all_rels_good[ss_id]:
                    #     for lex in wn.keys():
                    #         if wn[lex]['syns'][target]['ili_key']:
                    #             good_link_to_ili = True

                    # for target in all_rels_warn[ss_id]:
                    #     for lex in wn.keys():
                    #         if wn[lex]['syns'][target]['ili_key']:
                    #             weak_link_to_ili = True

                    # if good_link_to_ili == False and weak_link_to_ili == True:
                    #     vr_lex['synsets_ili_lnk_warn_lbl_val'].append(ss_id)
                    #     vr_lex['synsets_ili_lnk_warn_lbl'] = False
                    #     final_validation = False

                    # elif good_link_to_ili == False and weak_link_to_ili == False:
                    #     vr_lex['synsets_ili_lnk_bad_lbl_val'].append(ss_id)
                    #     vr_lex['synsets_ili_lnk_bad_lbl'] = False
                    #     final_validation = False
                ################################################################


            # FINAL VALIDATION
            vr['final_validation'] = final_validation
            ### LOG     
            # print("""ILI defs and links checked for {}
            # \tResult is {}\t{}""".format(lexicon,
            #                              final_validation,
            #                              dt.today().isoformat()))


        else:
            wn = None
            wn_dtls = None
        return vr, filename, wn, wn_dtls


    def confirmUpload(filename=None, u=None):

        try:

            # print("\n")   #TEST
            # print("ENTERING 1st Iteration")   #TEST
            # print("\n")   #TEST


            l = lambda:dd(l)
            r = l()  # report
            r['new_ili_ids'] = []

            # OPEN FILE
            if filename.endswith('.xml'):
                wn = open(os.path.join(app.config['UPLOAD_FOLDER'],
                                       filename), 'rb')
                wnlmf = etree.XML(wn.read())

            elif filename.endswith('.gz'):
                with gzip.open(os.path.join(app.config['UPLOAD_FOLDER'],
                                            filename), 'rb') as wn:
                    wnlmf = etree.XML(wn.read())


            # PARSE WN & GET ALL NEEDED
            src_id = fetch_src()
            ssrels = fetch_ssrel()
            langs, langs_code = fetch_langs()
            poss = fetch_pos()
            wn, wn_dtls = parse_wn(wnlmf)

            for lexicon in  wn.keys():

                proj_id = f_proj_id_by_code(lexicon)
                lang = wn[lexicon]['attrs']['language']
                lang_id = langs_code['code'][lang]
                version = wn[lexicon]['attrs']['version']
                lex_conf = float(wn[lexicon]['attrs']['confidenceScore'])

                ################################################################
                # CREATE NEW SOURCE BASED ON PROJECT+VERSION
                ################################################################
                src_id = insert_src(int(proj_id), version, u)
                wn[lexicon]['src_id'] = src_id

                ################################################################
                # BULK INSERT SOURCE META
                ################################################################
                blk_src_data = [] # [(src_id, attr, val, u),...]
                for attr, val in wn[lexicon]['attrs'].items():
                    blk_src_data.append((src_id, attr, val, u))
                blk_insert_src_meta(blk_src_data)


                ################################################################
                # GATHER NEW ILI CANDIDATES
                ################################################################
                max_ili_id = fetch_max_ili_id()
                blk_ili_data = []
                # (id, kind, ili_def, status, src_id, origin_key, u)
                for new_ili in wn_dtls['ss_ili_new'][lexicon]:
                    ili_key = max_ili_id + 1
                    synset = wn[lexicon]['syns'][new_ili]

                    status = 2 # TEMPORARY
                    kind = synset['ili_kind']
                    ili_def = None
                    for (l, d) in synset['ili_def'].keys():
                        ili_def = d
                    origin_key = synset['ili_origin_key']

                    blk_ili_data.append((ili_key, kind, ili_def, status,
                                         src_id, origin_key, u))

                    synset['ili_key'] = ili_key
                    r['new_ili_ids'].append(ili_key)
                    max_ili_id = ili_key

                ################################################################
                # WRITE NEW ILI CANDIDATES TO DB
                ################################################################
                blk_insert_into_ili(blk_ili_data)
                ################################################################



                ################################################################
                # GATHER NEW SYNSETS: NEW ILI CONCEPTS + OUT OF ILI CONCEPTS
                ################################################################
                blk_ss_data = list()
                blk_ss_src_data = list()
                blk_def_data = list()
                blk_def_src_data = list()
                blk_ssexe_data = list()
                blk_ssexe_src_data = list()
                max_ss_id = fetch_max_ss_id()
                max_def_id = fetch_max_def_id()
                max_ssexe_id = fetch_max_ssexe_id()
                for new_ss in wn_dtls['ss_ili_new'][lexicon] + \
                              wn_dtls['ss_ili_out'][lexicon]:

                    synset = wn[lexicon]['syns'][new_ss]
                    origin_key = synset['ili_origin_key']
                    ili_id = synset['ili_key']
                    ss_pos = poss['tag'][synset['SSPOS']]

                    ss_id = max_ss_id + 1
                    synset['omw_ss_key'] = ss_id

                    try:
                        ss_conf = float(synset['attrs']['confidenceScore'])
                    except:
                        ss_conf = lex_conf

                    blk_ss_data.append((ss_id, ili_id, ss_pos, u))

                    blk_ss_src_data.append((ss_id, src_id, origin_key,
                                            ss_conf, u))


                    ############################################################
                    # DEFINITIONS
                    ############################################################
                    for (def_lang_id, def_txt) in synset['def'].keys():


                        def_id = max_def_id + 1


                        # if def_id and ss_id and def_lang_id and def_txt and u: #TEST
                        #     test = True #TEST
                        # else: #TEST
                        #     print(def_id, ss_id, def_lang_id, def_txt, u) #TEST


                        blk_def_data.append((def_id, ss_id, def_lang_id, def_txt, u))



                        try:
                            wn_def = synset['def'][(def_lang_id, def_txt)]
                            def_conf = float(wn_def['attrs']['confidenceScore'])
                        except:
                            def_conf = ss_conf

                        blk_def_src_data.append((def_id, src_id, def_conf, u))

                        max_def_id = def_id

                    ############################################################
                    # EXAMPLES
                    ############################################################
                    for (exe_lang_id, exe_txt) in synset['ex'].keys():
                        exe_id = max_ssexe_id + 1

                        blk_ssexe_data.append((exe_id, ss_id, exe_lang_id,
                                               exe_txt, u))

                        try:
                            wn_exe = synset['ex'][(exe_lang_id, exe_txt)]
                            exe_conf = float(wn_exe['attrs']['confidenceScore'])
                        except:
                            exe_conf = ss_conf

                        blk_ssexe_src_data.append((exe_id, src_id, exe_conf, u))

                        max_ssexe_id = exe_id

                    max_ss_id = ss_id  # Update max_ss_id

                ################################################################
                # WRITE NEW SYNSETS TO DB
                ################################################################
                blk_insert_omw_ss(blk_ss_data)
                blk_insert_omw_ss_src(blk_ss_src_data)
                blk_insert_omw_def(blk_def_data)
                blk_insert_omw_def_src(blk_def_src_data)
                blk_insert_omw_ssexe(blk_ssexe_data)
                blk_insert_omw_ssexe_src(blk_ssexe_src_data)
                ################################################################


                ################################################################
                # UPDATE OLD SYNSETS IN OMW (E.G. SOURCE, DEFs, EXEs, etc.)
                ################################################################
                # NOTE: IF THE OLD SYNSET HAS A DIFFERENT POS, IT SHOULD BE
                #       CONSIDERED A NEW SYNSET, BUT LINKED TO THE SAME ILI.
                ################################################################
                blk_ss_data = list()
                blk_ss_src_data = list()
                blk_def_data = list()
                blk_def_data_unique = set()
                blk_def_src_data = list()
                blk_ssexe_data = list()
                blk_ssexe_src_data = list()

                ili_ss_map = f_ili_ss_id_map()
                defs = fetch_all_defs_by_ss_lang_text()
                ssexes = fetch_all_ssexe_by_ss_lang_text()

                max_ss_id = fetch_max_ss_id()
                max_def_id = fetch_max_def_id()
                max_ssexe_id = fetch_max_ssexe_id()
                for linked_ss in wn_dtls['ss_ili_linked'][lexicon]:

                    synset = wn[lexicon]['syns'][linked_ss]
                    ss_pos = poss['tag'][synset['SSPOS']]
                    origin_key = synset['ili_origin_key']
                    ili_id = synset['ili_key']

                    try:
                        ss_conf = float(synset['attrs']['confidenceScore'])
                    except:
                        ss_conf = lex_conf

                    ############################################################
                    # FETCH ALL OMW SYNSETS LINKED TO THIS ILI ID
                    ############################################################
                    linked_ss_ids = ili_ss_map['ili'][ili_id]

                    ############################################################
                    # 2 CASES: SAME POS = SHARE SS, DIFFERENT POS = NEW SS
                    ############################################################
                    ss_id = None
                    for (ss, pos) in linked_ss_ids:
                        if pos == ss_pos:
                            ss_id = ss

                    ############################################################
                    # IF POS MATCH >> UPDATE OLD OMW SYNSET
                    ############################################################
                    if ss_id:

                        synset['omw_ss_key'] = ss_id

                        blk_ss_src_data.append((ss_id, src_id,
                                                origin_key, ss_conf, u))

                        ########################################################
                        # DEFINITIONS
                        ########################################################
                        for (def_lang_id, def_txt) in synset['def'].keys():

                            try:
                                def_id = defs[ss_id][(def_lang_id, def_txt)]
                            except:
                                def_id = None

                            if not def_id:

                                # avoid duplicates linking to the same omw_concept
                                if (ss_id, def_lang_id, def_txt) not in blk_def_data_unique:

                                    def_id = max_def_id + 1

                                    # if def_id and ss_id and def_lang_id and def_txt and u: #TEST
                                    #     test = True #TEST
                                    # else: #TEST
                                    #     print(def_id, ss_id, def_lang_id, def_txt, u) #TEST

                                    blk_def_data_unique.add((ss_id, def_lang_id, def_txt))
                                    blk_def_data.append((def_id, ss_id, def_lang_id,
                                                 def_txt, u))
                                    max_def_id = def_id

                                    try:
                                        wn_def = synset['def'][(def_lang_id, def_txt)]
                                        def_conf = float(wn_def['attrs']['confidenceScore'])
                                    except:
                                        def_conf = ss_conf

                                    blk_def_src_data.append((def_id, src_id,
                                                            def_conf, u))


                                else:
                                    def_id = max_def_id
                                    # print((ss_id, def_lang_id,def_txt)) #TEST #IGNORED

                                max_def_id = def_id




                        ############################################################
                        # EXAMPLES
                        ############################################################
                        for (exe_lang_id, exe_txt) in synset['ex'].keys():

                            try:
                                exe_id = ssexes[ss_id][(exe_lang_id, exe_txt)]
                            except:
                                exe_id = None

                            if not exe_id:
                                exe_id = max_ssexe_id + 1
                                blk_ssexe_data.append((exe_id, ss_id, exe_lang_id,
                                                   exe_txt, u))
                                max_ssexe_id = exe_id

                            try:
                                wn_exe = synset['ex'][(exe_lang_id, exe_txt)]
                                exe_conf = float(wn_exe['attrs']['confidenceScore'])
                            except:
                                exe_conf = ss_conf

                            blk_ssexe_src_data.append((exe_id, src_id, exe_conf, u))

                    ############################################################
                    # NO POS MATCH >> CREATE NEW SYNSET
                    ############################################################
                    else:
                        ss_id = max_ss_id + 1
                        synset['omw_ss_key'] = ss_id

                        blk_ss_data.append((ss_id, ili_id, ss_pos, u))
                        blk_ss_src_data.append((ss_id, src_id, origin_key,
                                                ss_conf, u))

                        ############################################################
                        # DEFINITIONS
                        ############################################################
                        for (def_lang_id, def_txt) in synset['def'].keys():


                            # avoid duplicates linking to the same omw_concept
                            if (ss_id, def_lang_id,def_txt) not in blk_def_data_unique:

                                def_id = max_def_id + 1

                                # if def_id and ss_id and def_lang_id and def_txt and u: #TEST
                                #     test = True #TEST
                                # else: #TEST
                                #     print(def_id, ss_id, def_lang_id, def_txt, u) #TEST

                                blk_def_data_unique.add((ss_id, def_lang_id,def_txt))
                                blk_def_data.append((def_id, ss_id, def_lang_id,
                                             def_txt, u))
                                max_def_id = def_id


                                try:
                                    wn_def = synset['def'][(def_lang_id, def_txt)]
                                    def_conf = float(wn_def['attrs']['confidenceScore'])
                                except:
                                    def_conf = ss_conf

                                blk_def_src_data.append((def_id, src_id, def_conf, u))

                            else:
                                def_id = max_def_id
                                # print((ss_id, def_lang_id,def_txt)) #TEST #IGNORED


                            max_def_id = def_id

                        ############################################################
                        # EXAMPLES
                        ############################################################
                        for (exe_lang_id, exe_txt) in synset['ex'].keys():
                            exe_id = max_ssexe_id + 1

                            blk_ssexe_data.append((exe_id, ss_id, exe_lang_id,
                                                   exe_txt, u))

                            try:
                                wn_exe = synset['ex'][(exe_lang_id, exe_txt)]
                                exe_conf = float(wn_exe['attrs']['confidenceScore'])
                            except:
                                exe_conf = ss_conf

                            blk_ssexe_src_data.append((exe_id, src_id, exe_conf, u))

                            max_ssexe_id = exe_id

                        max_ss_id = ss_id  # Update max_ss_id



                ################################################################
                # INSERT/UPDATE ILI LINKED SYNSETS IN DB
                ################################################################
                blk_insert_omw_ss(blk_ss_data)
                blk_insert_omw_ss_src(blk_ss_src_data)
                blk_insert_omw_def(blk_def_data)
                blk_insert_omw_def_src(blk_def_src_data)
                blk_insert_omw_ssexe(blk_ssexe_data)
                blk_insert_omw_ssexe_src(blk_ssexe_src_data)
                ################################################################



            # print("\n")   #TEST
            # print("ENTERING 2nd Iteration")   #TEST
            # print(r)   #TEST
            # print("\n")   #TEST
            ################################################################
            # 2nd ITERATION: LEXICAL ENTRIES
            ################################################################
            for lexicon in  wn.keys():

                proj_id = f_proj_id_by_code(lexicon)
                lang = wn[lexicon]['attrs']['language']
                lang_id = langs_code['code'][lang]
                version = wn[lexicon]['attrs']['version']
                lex_conf = float(wn[lexicon]['attrs']['confidenceScore'])


                ################################################################
                # INSERT LEXICAL ENTRIES IN DB   - FIXME, ADD TAGS & script
                ################################################################
                blk_f_data = list()
                blk_f_src_data = list()
                blk_w_data = list()
                blk_wf_data = list()
                blk_sense_data = list()
                blk_sense_src_data = list()

                max_f_id = fetch_max_f_id()
                max_w_id = fetch_max_w_id()
                max_s_id = fetch_max_s_id()
                forms = fetch_all_forms_by_lang_pos_lemma()

                for le_id in wn[lexicon]['le'].keys():
                    wn_le = wn[lexicon]['le'][le_id]
                    pos = wn_le['lemma']['attrs']['partOfSpeech']
                    pos_id = poss['tag'][pos]
                    lemma = wn_le['lemma']['attrs']['writtenForm']

                    try:
                        le_conf = float(wn_le['attrs']['confidenceScore'])
                    except:
                        le_conf = lex_conf

                    try:
                        can_f_id = forms[lang_id][(pos_id,lemma)]
                    except:
                        can_f_id = None

                    if not can_f_id:
                        can_f_id = max_f_id + 1
                        blk_f_data.append((can_f_id, lang_id,
                                           pos_id, lemma, u))
                        max_f_id = can_f_id

                        w_id = max_w_id + 1
                        blk_w_data.append((w_id, can_f_id, u))
                        blk_wf_data.append((w_id, can_f_id, src_id,
                                            le_conf, u))
                        max_w_id = w_id

                    else: # New word (no way to know if the word existed!) FIXME!?
                        w_id = max_w_id + 1
                        blk_w_data.append((w_id, can_f_id, u))
                        blk_wf_data.append((w_id, can_f_id, src_id,
                                            le_conf, u))
                        max_w_id = w_id

                    blk_f_src_data.append((can_f_id, src_id, le_conf, u))


                    # ADD OTHER FORMS OF THE SAME WORD
                    for (lem_form_w, lem_form_script) in wn_le['forms'].keys():

                        try:
                            f_id = forms[lang_id][(pos_id,lem_form_w)]
                        except:
                            f_id = None
                        if not f_id:
                            f_id = max_f_id + 1
                            blk_f_data.append((f_id, lang_id,
                                               pos_id, lem_form_w, u))
                            max_f_id = f_id

                        # Always link to word
                        blk_wf_data.append((w_id, f_id, src_id,
                                            le_conf, u))


                    # ADD SENSES
                    for (sens_id, sens_synset) in wn_le['senses'].keys():
                        wn_sens = wn_le['senses'][(sens_id, sens_synset)]
                        try:
                            sens_conf = float(wn_sens['attrs']['confidenceScore'])
                        except:
                            sens_conf = le_conf


                        synset = wn[lexicon]['syns'][sens_synset]
                        ss_id = synset['omw_ss_key']

                        s_id = max_s_id + 1
                        blk_sense_data.append((s_id, ss_id, w_id, u))
                        max_s_id = s_id
                        blk_sense_src_data.append((s_id, src_id, sens_conf, u))


                    # FIXME! ADD Form.Script
                    # FIXME! ADD SenseRels, SenseExamples, Counts
                    # FIXME! ADD SyntacticBehaviour

                ################################################################
                # INSERT LEXICAL ENTRIES IN DB
                ################################################################
                blk_insert_omw_f(blk_f_data)
                blk_insert_omw_f_src(blk_f_src_data)
                blk_insert_omw_w(blk_w_data)
                blk_insert_omw_wf_link(blk_wf_data)
                blk_insert_omw_s(blk_sense_data)
                blk_insert_omw_s_src(blk_sense_src_data)
                ################################################################



            # print("\n")   #TEST
            # print("ENTERING 3rd Iteration")   #TEST
            # print(r)   #TEST
            # print("\n")   #TEST
            ############################################################
            # 3rd ITTERATION: AFTER ALL SYNSETS WERE CREATED
            ############################################################
            # SSREL (SYNSET RELATIONS)   FIXME, ADD SENSE-RELS
            ############################################################
            ili_ss_map = f_ili_ss_id_map()
            sslinks = fetch_all_ssrels_by_ss_rel_trgt()
            blk_sslinks_data = list()
            blk_sslinks_data_unique = set()
            blk_sslinks_src_data = list()
            max_sslink_id = fetch_max_sslink_id()
            for lexicon in wn.keys():
                src_id = wn[lexicon]['src_id']
                lang = wn[lexicon]['attrs']['language']
                lang_id = langs_code['code'][lang]
                lex_conf = float(wn[lexicon]['attrs']['confidenceScore'])

                for new_ss in wn_dtls['ss_ili_new'][lexicon] + \
                              wn_dtls['ss_ili_out'][lexicon]:
                    synset = wn[lexicon]['syns'][new_ss]
                    ss1_id = synset['omw_ss_key']

                    try:
                        ss_conf = float(synset['attrs']['confidenceScore'])
                    except:
                        ss_conf = lex_conf

                    for (rel, trgt) in synset['ssrel'].keys():

                        lex2 = trgt.split('-')[0]
                        synset2 = wn[lex2]['syns'][trgt]
                        ss2_id = synset2['omw_ss_key']
                        ssrel_id = ssrels['rel'][rel][0]


                        if (ss1_id, ssrel_id, ss2_id) not in blk_sslinks_data_unique:
                            blk_sslinks_data_unique.add((ss1_id, ssrel_id, ss2_id))

                            sslink_id = max_sslink_id + 1
                            blk_sslinks_data.append((sslink_id, ss1_id, ssrel_id,
                                                     ss2_id, u))

                            try:
                                sslink_attrs = synset['ssrel'][(rel, trgt)]['attrs']
                                sslink_conf = float(sslink_attrs['confidenceScore'])
                            except:
                                sslink_conf = ss_conf


                            blk_sslinks_src_data.append((sslink_id, src_id,
                                                         sslink_conf, lang_id, u))

                        else:
                            sslink_id = max_sslink_id
                            # print((ss1_id, ssrel_id, ss2_id)) #TEST #IGNORED

                        max_sslink_id = sslink_id




                ############################################################
                # IN THIS CASE WE NEED TO FIND WHICH MAP IT RECEIVED ABOVE
                ############################################################
                for linked_ss in wn_dtls['ss_ili_linked'][lexicon]:

                    synset = wn[lexicon]['syns'][linked_ss]
                    ss_pos = poss['tag'][synset['SSPOS']]
                    origin_key = synset['ili_origin_key']
                    ili_id = synset['ili_key']

                    ############################################################
                    # FETCH ALL OMW SYNSETS LINKED TO THIS ILI ID
                    ############################################################
                    linked_ss_ids = ili_ss_map['ili'][ili_id]

                    ss_id = None
                    for (ss, pos) in linked_ss_ids: # THERE MUST BE ONE!
                        if pos == ss_pos:
                            linked_ss = ss


                    synset = wn[lexicon]['syns'][linked_ss]
                    ss1_id = synset['omw_ss_key']

                    try:
                        ss_conf = float(synset['attrs']['confidenceScore'])
                    except:
                        ss_conf = lex_conf



                    for (rel, trgt) in synset['ssrel'].keys():

                        lex2 = trgt.split('-')[0]
                        synset2 = wn[lex2]['syns'][trgt]
                        ss2_id = synset2['omw_ss_key']
                        ssrel_id = ssrels['rel'][rel][0]



                        if (ss1_id, ssrel_id, ss2_id) not in blk_sslinks_data_unique:
                            blk_sslinks_data_unique.add((ss1_id, ssrel_id, ss2_id))


                            sslink_id = sslinks[ss1_id][(ssrel_id, ss2_id)]
                            if not sslink_id:
                                sslink_id = max_sslink_id + 1
                                blk_sslinks_data.append((sslink_id, ss1_id,
                                                         ssrel_id, ss2_id, u))
                                max_sslink_id = sslink_id


                            try:
                                sslink_attrs = synset['ssrel'][(rel, trgt)]['attrs']
                                sslink_conf = float(sslink_attrs['confidenceScore'])
                            except:
                                sslink_conf = ss_conf

                            blk_sslinks_src_data.append((sslink_id, src_id,
                                                         sslink_conf, lang_id, u))


                        else:
                            sslink_id = max_sslink_id
                            # print((ss1_id, ssrel_id, ss2_id)) #TEST #IGNORED


            ################################################################
            # INSERT SSRELS INTO THE DB
            ################################################################
            blk_insert_omw_sslink(blk_sslinks_data)
            blk_insert_omw_sslink_src(blk_sslinks_src_data)
            ################################################################




            return r
        except:
            return False
