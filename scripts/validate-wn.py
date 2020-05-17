#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Validate a file using the command line
#  Assume the user is '1' (admin)
#
# FIXME: should I also copy the file to public upoads?
#
#

import sys, os
import json
from omw import (
    app,
    g,
    uploadFile,
    validateFile,
    ingest_wordnet,
    connect_omw,
    updateLabels
)
import argparse

userid=1
parser = argparse.ArgumentParser(
    description='A program to make wordnet LMF from OMW 1.0 tsv',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

# It takes one argument: the name of the wordnet LMF file (can be gzipped)
parser.add_argument(
    'wnfile', help='WN-LMF.xml(.gz) to be loaded')
parser.add_argument('--auto-upload',  action="store_true",
                    help='Automatically upload the WN if it validates')
parser.add_argument('--no-upload', action="store_true",
                    help="Don't ask to upload the WN even if it validates")
parser.add_argument('--no-add-proj', action="store_true",
                    help="Don't automatically add the project")
args = parser.parse_args()



u =  sys.argv[0]
wnfile = args.wnfile

debug=sys.stderr
with app.app_context():
    g.omw = connect_omw()
    print("Validating file {} as user {}".format(wnfile,userid),
          file=debug)
    basename = os.path.basename(wnfile).rstrip('.gz').rstrip('.xml')
    vr, filename, wn, wn_dtls = validateFile(userid, wnfile,
                                             addproj = not args.no_add_proj)
    with open(basename+'.vr.json', 'w') as fh:
        json.dump(vr, fh, indent=2)
    with open(basename+'.wn_dtls.json', 'w') as fh:
        json.dump(wn_dtls, fh, indent=2)
    if vr["final_validation"]:
        uploadme=False
        print ("\n{} was validated\n".format(filename), file=debug)
        if not args.no_upload:
            if args.auto_upload:
                uploadme=True
            else:        
                user_input = input("Load into the Database? y/N\n")
                if user_input.lower() == 'y':
                    uploadme=True
            if uploadme:
                # copy the file into the uploads directory
                passed, filename = uploadFile('admin', wnfile, 'localfile')
                r =  ingest_wordnet(filename=filename, u=userid)
                if r:
                    with open(basename+'.upload.json', 'w') as fh:
                        json.dump(r, fh, indent=2)
                        updateLabels()
                        print ("\n{} was entered into the database\n".format(filename), file=debug)
                        print("see {}.upload.json for details of upload".format(basename), file=debug)
                
    else: 
        print ("\n{} was NOT validated\n".format(filename), file=debug)
    print("see {}.vr.json for details of validation".format(basename), file=debug)
    print("see {}.wn_dtls.json for details of wordnet".format(basename), file=debug)
    g.omw.close()
