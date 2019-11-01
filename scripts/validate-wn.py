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
    validateFile,
    ingest_wordnet,
    connect_omw,
    updateLabels
)

userid=1

# It takes one argument: the name of the wordnet LMF file (can be gzipped)
if (len(sys.argv) != 2):
    sys.stderr.write('usage: validate-wn.py WN-LMF.xml(.gz)\n')
    sys.exit(1)
else:
    u =  sys.argv[0]
    wnfile = sys.argv[1]

debug=sys.stderr
with app.app_context():
    g.omw = connect_omw()
    print("Validating file {} as user {}".format(wnfile,userid),
          file=debug)
    basename = os.path.basename(wnfile).rstrip('.gz').rstrip('.xml')
    vr, filename, wn, wn_dtls = validateFile(userid, wnfile)
    with open(basename+'.vr.json', 'w') as fh:
        json.dump(vr, fh, indent=2)
    with open(basename+'.wn_dtls.json', 'w') as fh:
        json.dump(wn_dtls, fh, indent=2)
    if vr["final_validation"]:
        print ("\n{} was validated\n".format(filename), file=debug)
        user_input = input("Load into the Database? y/N\n")
        if user_input.lower() == 'y':
            r =  ingest_wordnet(filename=wnfile, u=userid)
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
