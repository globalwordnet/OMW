#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import sys
from shutil import copyfile
import re
import urllib
import gzip
from collections import defaultdict as dd
from datetime import datetime as dt

from flask import request
from werkzeug.utils import secure_filename
from lxml import etree
from packaging.version import Version, InvalidVersion
import networkx as nx

from omw import app
from omw.omw_sql import *


ALLOWED_EXTENSIONS = set(['xml','gz','xml.gz'])

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
    ## FCB must be a better way than a global variable!
    ilimap=dict() # ili[ss_id] = 'i'.format(ili_id)
    ## try to use the same abbreviations as the SPDX organization
    ## https://spdx.org/licenses/
    licenses = {'wordnet':'wordnet',
                'https://wordnet.princeton.edu/license-and-commercial-use':'wordnet',
                'http://opendefinition.org/licenses/odc-by/':'ODC-BY',
                'http://www.cecill.info/licenses/Licence_CeCILL-C_V1-en.html':'CeCILL-1.0',
                "https://creativecommons.org/publicdomain/zero/1.0/":'CC0-1.0',
                "https://creativecommons.org/licenses/by/":'CC-BY',
                "https://creativecommons.org/licenses/by-sa/":'CC-BY-SA',
                "https://creativecommons.org/licenses/by/3.0/":'CC-BY-3.0',
                "https://creativecommons.org/licenses/by-sa/3.0/":'CC-BY-SA 3.0',
                "https://creativecommons.org/licenses/by/4.0/":'CC-BY-4.0',
                "https://creativecommons.org/licenses/by-sa/4.0/":'CC-BY-SA 4.0',
                'https://opensource.org/licenses/MIT/':'MIT',
                'https://opensource.org/licenses/Apache-2.0':'Apache-2.0',
                'https://www.unicode.org/license.html':'unicode'}
    mindefchars=20
    mindefwords=4
    
    def fetch_licenses():
        return licenses
    
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
        # 1st ITERATION: LEXICAL ENTRIES
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
                        relTrgt = sensRel.get('target')
                        relType = sensRel.get('relType')

                        wn_sensRels = wn_sens['rels'][(relType, relTrgt)]
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

                    ############################################################
                    # One sense can have multiple counts from different sources;  
                    # This info is inside ['attrs'], if provided.
                    #
                    # We need to enumerate them because we can have:
                    #   <Count dc:source="SemCor">50</Count>
                    #   <Count dc:source="NTUMC">50</Count>
                    ############################################################
                    for i, sensCount in enumerate(sense.findall('Count')):
                        sensCount_txt = sensCount.text
                        if sensCount_txt: # if <Count></Count> is not empty
                            wn_sensCounts = wn_sens['counts'][(i,sensCount_txt)]
                            wn_sensCounts['attrs'] = sensCount.attrib


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
        # 2n ITTERATION: SYNSETS
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
                for s_lexicon, le_id in synset_senses[ss_id].keys():
                    syn_pos.add(synset_senses[ss_id][(s_lexicon,le_id)])

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
                        ilimap[ss_id] = 'i{}'.format(ili_id)   ### use for merging graphs
                        #print(ss_id,ilimap[ss_id], file=sys.stderr)
                        #ilis.add(ss_id)   ### FCB
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


    def uploadFile(current_user, thing, ftype):
        """
        Given a file to upload, give it a unique name and upload it!
        files can come from:
        ftype      source 
        webfile    a file to be uploaded
        url        a url with (we hope) a wordnet
        localfile  a file given by the path on the local system

        We give the files a secure name made up of:
        the date, the user who uploaded it, and the original filename
        e.g.
        2020-02-23T084411_admin_islwn.xml
        """
        
        dtformat = "%Y-%m-%dT%H:%M:%S"
        now = dt.utcnow().strftime(dtformat)
        upload_folder = app.config['UPLOAD_FOLDER']

        if ftype == 'webfile' and allowed_file(thing.filename):
            filename = now + '_' +str(current_user) + '_' + thing.filename
            filename = secure_filename(filename)
            thing.save(os.path.join(upload_folder, filename))
            file_uploaded = True

        elif ftype == 'url':
            file = urllib.urlopen(thing)
            basename = os.path.basename(thing)
            filename = now + '_' +str(current_user) + '_' + basename
            filename = secure_filename(filename)

            if file and allowed_file(filename):
                open(os.path.join(upload_folder, filename),
                     'wb').write(file.read())
            file_uploaded = True
        elif ftype == 'localfile':
            basename = os.path.basename(thing)
            filename = now + '_' +str(current_user) + '_' + basename
            filename = secure_filename(filename)
            try:
                copyfile(thing, os.path.join(upload_folder, filename))
                file_uploaded = True
            except IOError as e:
                print("Unable to copy file. %s" % e)
        else:
            filename = None
            file_uploaded = False

        return file_uploaded, filename



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
                        


    def findBadSenseRelations(wn):    #FIXME must add the message in the template
        badlinks = []
        all_synset_ids = []
        all_sense_ids = []
        for lexicon in wn.keys():
            #print(lexicon)
            #print(len(wn[lexicon]['syns'].keys()))
            # print(wn[lexicon]['syns'].keys(), file=sys.stderr) #TEST
            all_synset_ids += wn[lexicon]['syns'].keys()

            for le_id in wn[lexicon]['le'].keys():
                for sens_id, sens_synset in wn[lexicon]['le'][le_id]['senses']:
                    all_sense_ids.append(sens_id)

        # looping again to find the sense-rels
        for lexicon in wn.keys():
            for le_id in wn[lexicon]['le'].keys():
                # print(wn[lexicon]['le'][le_id]['senses'], file=sys.stderr) #TEST
                for sens_id, sens_synset in wn[lexicon]['le'][le_id]['senses']:
                    for relType, relTrgt in wn[lexicon]['le'][le_id]['senses'][(sens_id, sens_synset)]['rels']:
                        if relTrgt not in (all_synset_ids + all_sense_ids):
                            badlinks.append((sens_id, relType, relTrgt))


        # print(all_synset_ids, file=sys.stderr)
        # print(all_sense_ids, file=sys.stderr)
        # print("bad: ", badlinks, file=sys.stderr)
        return badlinks

    def openWN(filename):
        """
        Open an XML file, possibly compressed, 
        return the filehandle or None if you couldn't find it
        """
        wnfile = None
        if os.path.exists(filename):
            wnfile = filename
        elif os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'],
                                         filename)):
            wnfile = os.path.join(app.config['UPLOAD_FOLDER'],
                                  filename)
        if wnfile:
            if filename.endswith('.xml'):
                    wnfh = open(wnfile, 'rb')
            elif filename.endswith('.gz'):
                 wnfh = gzip.open(wnfile, 'rb')
            return  wnfile, wnfh
        else:
            return None, None
    

    def validateFile(current_user, filename, addproj=False):
        """
        Read a file, either *.xml or *.gz
        Validate against the DTD

        addproj=True
        If you want to automatically add the project.
        This is useful for bulk entry from the commandline

        """
        l=lambda:dd(l)
        vr = l()  # validation report
        final_validation = True # assume it will pass
        vr['filename']=filename
        vr['upload'] = True
        
        ###LOG
        print('Preparing to Validate File\t{}\t{}'.format(filename,dt.today().isoformat()),
              file=sys.stderr)
       
 
        ########################################################################
        # CHECK WN STRUCTURE (MATCH AGAINST DTD)
        ########################################################################

        ### find and open the wordnet
        
        wnlocation, wnfh = openWN(filename)
        vr['location'] = wnlocation 
        if wnlocation:
            wnlmf = etree.XML(wnfh.read())
            vr['read'] = True
        else:
            print(f"Could not find {filename}, \
            looked here and in {app.config['UPLOAD_FOLDER']}",
                  file=sys.stderr)
            vr['read'] = False
            # vr, filename, wn, wn_dtls
            return vr, filename, None, None                         ### NO wordnet

        ### open the DTD then validate
        
        dtd_f = open(app.config['ILI_DTD'], 'rb')
        print('Opening DTD', app.config['ILI_DTD'],
              file=sys.stderr)
        dtd = etree.DTD(dtd_f)
        
        if dtd.validate(wnlmf):
            vr['dtd_val'] = True
            print('Validates against DTD', app.config['ILI_DTD'],
                  file=sys.stderr)
        else:
            vr['dtd_val'] = False
            vr['dtd_val_errors'] = str(dtd.error_log.filter_from_errors()[0])
            # vr, filename, wn, wn_dtls
            return vr, filename, None, None                         ### Not valid

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

            vr['bad_sense_rels'] = findBadSenseRelations(wn)
            if vr['bad_sense_rels']:
                final_validation = False

            for lexicon in wn:
                ### LOG     
                print('Checking {}\t{}'.format(lexicon,
                                               dt.today().isoformat()),
                      file=sys.stderr)

                vr_lex = vr['lexicon'][lexicon]

                ################################################################
                # CHECK META-DATA
                ################################################################
                lexicon_lbl = wn[lexicon]['attrs']['id']
                lexicon_id =  f_proj_id_by_code(lexicon_lbl)
                vr_lex['lex_lbl_val'] = lexicon_lbl
                if lexicon_lbl in projs.values():
                    vr_lex['lex_lbl'] = True
                elif addproj:
                    insert_new_project(lexicon_lbl,
                                       current_user)
                    print('Added Project:',  lexicon_lbl)
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

                version_string = wn[lexicon]['attrs']['version']
                vr_lex['version_lbl_val'] = version_string
                try:
                    if '-' in version_string:
                        raise InvalidVersion('hyphen in version string')
                    version = Version(version_string)
                except InvalidVersion:
                    vr_lex['valid_version'] = False
                    final_validation = False
                else:
                    normalized_version_string = str(version)
                    vr_lex['valid_version'] = True
                    if normalized_version_string != version_string:
                        vr_lex['version_lbl_val'] += " ({})".format(
                            normalized_version_string)
                    # check if version is newer than anything in the database
                    vr_lex['new_version'] = True
                    for src_id, proj_ver in fetch_src().items():
                        proj_id, src_ver = proj_ver
                        src_ver = Version(src_ver)
                        if (proj_id == lexicon_lbl and src_ver >= version):
                            vr_lex['new_version'] = False
                            final_validation = False
                            break

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
                if lic in licenses:
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
                #ilis = set(wn[lexicon]['syns'][target]['ili_key'] for i in ili.keys())
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
                        
                        # CHECK ILI DEFINITIONS' LENGTH and that it exists
                        if ili_def is None or (len(ili_def) < mindefchars) or \
                           (len(ili_def.split()) < mindefwords):
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
                    if checkLinked(lnks, good_rels, ilimap.keys(), ss_id, set()):
                        link_to_ili = 'good'
                        #print("LINKED g:",  link_to_ili, ss_id, file=debug)
                    # elif checkLinked(lnks, good_rels+warn_rels, ilis, ss_id, set()):
                    #     link_to_ili = 'weak'
                    #     vr_lex['synsets_ili_lnk_warn'].append(ss_id)
                    #     #print("LINKED w:",  link_to_ili, ss_id, file =debug)
                    elif checkLinked(lnks, good_rels+warn_rels+bad_rels,
                                     ilimap.keys(), ss_id, set()):
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

                ########################################################
                # Loops and cycles
                ########################################################
                print("Checking {} for loops and cycles".format(lexicon),file=sys.stderr)
                hypernym_rel_dict = dd(set)
                vr_lex["bad_loops"] = dd(list)
                #print("Checking for loops!")
                for s in wn[lexicon]['syns']:
                    for  (typ, trg) in wn[lexicon]['syns'][s]['ssrel']:
                        if s == trg:
                            vr_lex["bad_loops"][typ].append(s)
                        else:
                            if typ in ['hypernym', 'instance_hypernym']:
                                hypernym_rel_dict[s].add(trg)
                            elif typ in ['hyponym', 'instance_hyponym']:
                                hypernym_rel_dict[trg].add(s)
                                
                #print("Start with cycles!", lexicon)
                G =  nx.DiGraph(hypernym_rel_dict)
                #print("G",G.nodes(),G.edges(),hypernym_rel_dict,file=sys.stderr)
                vr_lex["bad_cycles"] = list(nx.simple_cycles(G))
                vr_lex["bad_cycles"].sort()
                if vr_lex["bad_cycles"] or  vr_lex["bad_loops"]:
                    final_validation = False
                ################################################
                # Check with complete graph
                ################################################
                print("Checking {} merged with OMW for cycles".format(lexicon),file=sys.stderr)
                OMW_rel_dict=fetch_graph(ili_labels=True)
                #print("Loaded OMW hypernym relations",file=sys.stderr)
                O = nx.DiGraph(OMW_rel_dict)
                #print("Made OMW graph",file=sys.stderr)
                Gi = nx.relabel_nodes(G,ilimap)
                #print("Gi",Gi.nodes(),Gi.edges(),file=sys.stderr)
                A = nx.compose(O,Gi)
                #print("Merged graphs",file=sys.stderr)
                bad_new = list(nx.simple_cycles(Gi))
                bad_merged = list(nx.simple_cycles(A))
                # print('bad_merged_new',  [c for c in bad_merged if c not in bad_new],
                #       file=sys.stderr)
                vr_lex["bad_merged_cycles"] = [c for c in bad_merged if c not in bad_new]
                if vr_lex["bad_merged_cycles"]:
                    final_validation = False          
                #print("Done with cycles!")
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


    def ingest_wordnet(filename=None, u=None):
        """
        Add the validated wordnet into the database and return a report.

        Args:
            filename: the temporary filename of the uploaded wordnet
            u: the user id of the user who uploaded the wordnet
        Returns:
            dict: a summary of the wordnet contents; if ingestion fails,
                `False` is returned
        """
        print("Loading {} (validated) into OMW".format(filename),file=sys.stderr)
        try:
            insert=True   ### really put stuff in the database
        
            # print("\n")   #TEST
            # print("ENTERING 1st Iteration", file=sys.stderr)   #TEST
            # print("\n")   #TEST
            

            l = lambda:dd(l)
            r = l()  # report
            r['new_ili_ids'] = []
            r['wns'] = []
            r['lang_ids'] = []


            ####################################################################
            # omw_synset_keys and omw_sense_keys store the OMW ID for each LMF
            # synset and sense, respectively. This is necessary because links
            # can exist across lexicons, and we need a structure that keeps
            # this info not nested inside each lexicon.
            #
            # usage (pass LMF ID as key):
            # omw_synset_keys['example-sv-1-n'] = 2
            # omw_synset_keys['example-sv-1-n-1'] = 30
            ####################################################################
            omw_synset_keys = dict()
            omw_sense_keys = dict()

            ### assume this is all good, as it has just been checked
            wnlocation, wnfh = openWN(filename)
            wnlmf = etree.XML(wnfh.read())
            print(f"Read wn at {wnlocation}", file=sys.stderr)
            
            # PARSE WN & GET ALL NEEDED
            src_id = fetch_src()
            ssrels = fetch_ssrel()
            srels = fetch_srel()
            langs, langs_code = fetch_langs()
            poss = fetch_pos()
            wn, wn_dtls = parse_wn(wnlmf)
            for lexicon in  wn.keys():
                print("Loading lexicon {}".format(lexicon),file=sys.stderr)
                proj_id = f_proj_id_by_code(lexicon)
                lang = wn[lexicon]['attrs']['language']
                lang_id = langs_code['code'][lang]
                version = wn[lexicon]['attrs']['version']
                r['wns'].append(lexicon + '-' +  version)
                r['lang_ids'].append(lang_id)
                lex_conf = float(wn[lexicon]['attrs']['confidenceScore'])
                wn[lexicon]['attrs']['filename'] = filename


                ################################################################
                # CREATE NEW SOURCE BASED ON PROJECT+VERSION
                ################################################################
                if insert:
                    src_id = insert_src(int(proj_id), version, u)
                wn[lexicon]['src_id'] = src_id

                ################################################################
                # BULK INSERT SOURCE META
                ################################################################
                blk_src_data = [] # [(src_id, attr, val, u),...]

                ### add date it was uploaded
                dtformat = "%Y-%m-%d %H:%M:%S"
                now = dt.utcnow().strftime(dtformat)
                wn[lexicon]['attrs']['uploaded'] = now
                
                for attr, val in wn[lexicon]['attrs'].items():
                    ### remove dc namespace ? should we keep as 'dc;'
                    if attr.startswith('{http://purl.org/dc/elements/1.1/}'):
                        attr = attr[34:]
                    blk_src_data.append((src_id, attr, val, u))
                if insert:
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
                if insert:
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
                    omw_synset_keys[new_ss] = ss_id

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
                if insert:
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

                        omw_synset_keys[linked_ss] = ss_id


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
                        omw_synset_keys[linked_ss] = ss_id

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
                if insert:
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
                blk_sense_counts_data = list()
                blk_sense_counts_src_data = list()

                max_f_id = fetch_max_f_id()
                max_w_id = fetch_max_w_id()
                max_s_id = fetch_max_s_id()
                max_sm_id = fetch_max_sm_id()
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

                    else: # New word (no way to know if the word existed!) #FIXME !?
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


                    ############################################################
                    # ADD SENSES
                    # - we link a synset_id to a word_id (LexicalEntry in LMF)
                    # - we read counts for each sense 
                    #
                    # - FIXME we don't yet import examples
                    # - FIXME we don't yet import definitions BECAUSE
                    #         they don't yet exist in the LMF (FCB wants this)
                    ############################################################
                    for (sens_id, sens_synset) in wn_le['senses'].keys():
                        wn_sens = wn_le['senses'][(sens_id, sens_synset)]

                        ########################################################
                        # Confidence order: sense, lexical-entry
                        ########################################################
                        if 'confidenceScore' in wn_sens['attrs'].keys():
                            sens_conf = float(wn_sens['attrs']['confidenceScore'])
                        else:
                            sens_conf = le_conf


                        ss_id = omw_synset_keys[sens_synset]
                        s_id = max_s_id + 1
                        omw_sense_keys[sens_id] = s_id

                        blk_sense_data.append((s_id, ss_id, w_id, u))
                        max_s_id = s_id
                        blk_sense_src_data.append((s_id, src_id, sens_conf, u))



                        ########################################################
                        # Counts should be stored in sm (sense-meta) and sm_src
                        # The table smt (sense-meta-tags) stores the meaning of
                        # each meta-tag;
                        #
                        # FIXME I'm assuming a hardcoded 1 for the frequency;
                        # This so far is true because we are inserting counts
                        # with PWN, so it was the first meta-tag; maybe we can
                        # confirm this in the code later; This assumption is
                        # hardcoded in other places too...
                        #
                        # FIXME, we are enforcing counts to be integers!
                        # this needs to be done in conjunction with some checks
                        ########################################################
                        for (i, count) in wn_sens['counts'].keys():
                            wn_sensCounts = wn_sens['counts'][(i, count)]

                            ####################################################
                            # Confidence order: count, sense
                            ####################################################
                            if 'confidenceScore' in wn_sensCounts['attrs'].keys():
                                count_conf = float(wn_sensCounts['attrs']['confidenceScore'])
                            else:
                                count_conf = sens_conf


                            sm_id = max_sm_id + 1
                            max_sm_id = sm_id

                            smt_id = 1  # FIXME, this is hardcoded 1 for 'freq'

                            blk_sense_counts_data.append((sm_id, s_id, smt_id, int(count), u))
                            blk_sense_counts_src_data.append((sm_id, src_id, count_conf, u))

                    # FIXME! ADD Form.Script
                    # FIXME! ADD SyntacticBehaviour

                ################################################################
                # INSERT LEXICAL ENTRIES IN DB
                ################################################################
                if insert:
                    blk_insert_omw_f(blk_f_data)
                    blk_insert_omw_f_src(blk_f_src_data)
                    blk_insert_omw_w(blk_w_data)
                    blk_insert_omw_wf_link(blk_wf_data)
                    blk_insert_omw_s(blk_sense_data)
                    blk_insert_omw_s_src(blk_sense_src_data)
                    blk_insert_omw_sm(blk_sense_counts_data)
                    blk_insert_omw_sm_src(blk_sense_counts_src_data)
                ################################################################



            ####################################################################
            # 3rd ITTERATION: AFTER ALL SYNSETS AND SENSE WERE CREATED
            #                 WE NOW CAN ADD RELATIONS BETWEEN THESE
            #
            # a) for each synset in the lexiccon, see and add what it links to
            # b) for each sense in the lexicon, see and add what it links to
            #    (senses are inside lexical entries)
            #
            # WARNING:
            # Things can link across lexicons; which means that synsets and
            # senses may link to things that  belong to lexicons other than the
            # one the source of the relation is;
            #
            # Links to things that are not synsets of senses should have been
            # caught before this moment;
            # Repeated links should also have been caught before this moment;
            ####################################################################

            blk_sslinks_data = list() # synset-synset links to write to db
            blk_sslinks_src_data = list()
            sslinks_db = fetch_all_ssrels_by_ss_rel_trgt() # sslinks already in db
            # example: sslinks_db[ss1_id][(ssrel_id,ss2_id)] = sslink_id

            blk_slinks_data = list() # sense-sense links to write to db
            blk_slinks_src_data = list()
            slinks_db = fetch_all_srels_by_s_rel_trgt() # slinks already in db
            # example: slinks_db[s1_id][(srel_id,s2_id)] = slink_id

            blk_ssslinks_data = list() # sense-synset links to write to db
            blk_ssslinks_src_data = list()
            ssslinks_db = fetch_all_sssrels_by_s_rel_trgt() # ssslinks already in db
            # example: ssslinks_db[s_id][(srel_id, ss_id)] = ssslink_id

            # get the max IDs from the db
            max_sslink_id = fetch_max_sslink_id()
            max_slink_id = fetch_max_slink_id()
            max_ssslink_id = 0 if (not fetch_max_ssslink_id()) else fetch_max_ssslink_id()
            print(max_ssslink_id)
            
            for lexicon in wn.keys():
                src_id = wn[lexicon]['src_id']
                lang = wn[lexicon]['attrs']['language']
                lang_id = langs_code['code'][lang]
                lex_conf = float(wn[lexicon]['attrs']['confidenceScore'])

                ################################################################
                # INSERT SYNSET RELATIONS (THESE ARE ONLY SYNSET-SYNSET)
                ################################################################
                for ss1 in wn[lexicon]['syns']: # each synset in the lexicon
                    synset1=wn[lexicon]['syns'][ss1]
                    for (rel, ss2) in synset1['ssrel']: # each link from the ss1
                        sslink = synset1['ssrel'][(rel, ss2)]

                        # Get the OMW IDs from the synsets
                        ss1_id = omw_synset_keys[ss1]
                        ss2_id = omw_synset_keys[ss2]
                        ssrel_id = ssrels['rel'][rel][0]

                        # Get confidenceScore for synset-synset relation
                        if 'confidenceScore' in sslink['attrs'].keys():
                            sslink_conf = float(sslink['attrs']['confidenceScore'])
                            # print("sslink had confidenceScore") #TEST
                        elif 'confidenceScore' in synset1['attrs'].keys():
                            sslink_conf = float(synset1['attrs']['confidenceScore'])
                            # print("sslink did not have confidenceScore, but the Synset did") #TEST
                        else:
                            sslink_conf = lex_conf
                            # print("neither sslink nor the synset had confidenceScore, using lexicon's") #TEST


                        ## see if we know this link
                        try:
                            ## known --- get id
                            sslink_id = sslinks_db[ss1_id][(ssrel_id,ss2_id)]
                        except:
                            ## new --- add link
                            max_sslink_id += 1
                            sslink_id = max_sslink_id
                            sslinks_db[ss1_id][(ssrel_id,ss2_id)] = max_sslink_id
                            blk_sslinks_data.append((sslink_id, ss1_id, ssrel_id,
                                                     ss2_id, u))

                        ## source the link
                        blk_sslinks_src_data.append((sslink_id, src_id,
                                                     sslink_conf, lang_id, u))
                        ## DEBUG
                        # print(ss1, ss1_id,
                        #       rel, ssrel_id,
                        #       ss2, ss2_id,
                        #       sslink_id, sslink_conf,
                        #       sslink_attrs)

                ################################################################
                # INSERT SENSE RELATIONS (IT CAN BE SENSE-SENSE, SENSE-SYNSET)
                ################################################################
                for le_id in wn[lexicon]['le'].keys():
                    wn_le = wn[lexicon]['le'][le_id]
                    for (sens_id, sens_synset) in wn_le['senses'].keys():
                        wn_sens = wn_le['senses'][(sens_id, sens_synset)]
                        sense_db_id = omw_sense_keys[sens_id]

                        for relType, relTrgt in wn_sens['rels']:
                            srel_db_id = srels['rel'][relType][0]
                            slink = wn_sens['rels'][(relType, relTrgt)]

                            # find the confidence of this slink
                            # (order: slink, sense, lexical entry, lexicon)
                            if 'confidenceScore' in slink['attrs'].keys():
                                slink_conf = float(slink['attrs']['confidenceScore'])
                            elif 'confidenceScore' in wn_sens['attrs'].keys():
                                slink_conf = float(wn_sens['attrs']['confidenceScore'])
                            elif 'confidenceScore' in wn_le['attrs'].keys():
                                slink_conf = float(wn_le['attrs']['confidenceScore'])
                            else:
                                slink_conf = lex_conf

                            ####################################################
                            # - See what kind of relation this is:
                            #   sense-sense, sense-synset
                            # - find or create a new db id
                            ####################################################
                            if relTrgt in omw_synset_keys.keys():
                                trgt_db_id = omw_synset_keys[relTrgt]

                                try:
                                    ssslink_db_id = ssslinks_db[sense_db_id][(srel_db_id, trgt_db_id)]
                                except:
                                    max_ssslink_id += 1
                                    ssslink_db_id = max_ssslink_id
                                    ssslinks_db[sense_db_id][(srel_db_id,trgt_db_id)] = max_ssslink_id
                                    blk_ssslinks_data.append((ssslink_db_id, sense_db_id,
                                                              srel_db_id, trgt_db_id, u))

                                blk_ssslinks_src_data.append((ssslink_db_id, src_id, slink_conf,
                                                              lang_id, u))

                            elif relTrgt in omw_sense_keys.keys():
                                trgt_db_id = omw_sense_keys[relTrgt]

                                try:
                                    slink_db_id = slinks_db[sense_db_id][(srel_db_id, trgt_db_id)]
                                except:
                                    max_slink_id += 1
                                    slink_db_id = max_slink_id
                                    slinks_db[sense_db_id][(srel_db_id,trgt_db_id)] = max_slink_id
                                    blk_slinks_data.append((slink_db_id, sense_db_id, srel_db_id,
                                                            trgt_db_id, u))

                                blk_slinks_src_data.append((slink_db_id, src_id, slink_conf, u))

                            else:
                                # should never happen, must be a check
                                print("sense-TARGET problem", file=sys.stderr)

            ################################################################
            # INSERT (synset-synset, sense-sense, sense-synset) LINKS INTO THE DB
            ################################################################
            if insert:
                blk_insert_omw_sslink(blk_sslinks_data)
                blk_insert_omw_sslink_src(blk_sslinks_src_data)

                blk_insert_omw_ssslink(blk_ssslinks_data)
                blk_insert_omw_ssslink_src(blk_ssslinks_src_data)

                blk_insert_omw_slink(blk_slinks_data)
                blk_insert_omw_slink_src(blk_slinks_src_data)
            ################################################################

            return r
        except:
            print("Failed to Load {} into OMW\n".format(filename), file=sys.stderr)
            return False
