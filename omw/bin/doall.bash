###############################################################################
# MAKE FRESH OMW.DB
###############################################################################

echo "Deleting old omw.db"
rm omw.db

echo "Creating new omw.db"
python3 make-omw-db.py


###############################################################################
# LOAD ILI DEPENDENCIES
###############################################################################

# LOAD KIND TAGS
echo "ILI: Loading kind data..."
python3 load-ili-kinds.py omw.db

# LOAD STATUS TAGS
echo "ILI: Loading status data..."
python3 load-ili-status.py omw.db


###############################################################################
# LOAD OMW DEPENDENCIES
###############################################################################

# LOAD POS TAGS
echo "Loading POS data..."
python3 load-pos.py omw.db

# LOAD SSRELS
echo "Loading SSREL data..."
python3 load-ssrels.py omw.db

# LOAD SRELS
echo "Loading SREL data..."
python3 load-srels.py omw.db


###############################################################################
# LOAD PWN3.0+ILI
###############################################################################
echo
echo "Loading PWN30..."
python3 load-pwn.py omw.db


###############################################################################
# LOAD/UPDATE PWN FREQUENCIES
###############################################################################
echo
echo
echo "Loading PWN30 frequencies..."
python3 load-pwn-freq.py omw.db
echo "Updating (all) frequencies..."
python3 update-freq.py omw.db


###############################################################################
# Update LABELS (FOR PWN)
###############################################################################
echo
echo "Loading PWN30 synset labels..."
python3 update-label.py omw.db


###############################################################################
# LOADING (ALL) OMW LANGUAGES
###############################################################################
echo
echo "Loading language data..."
python3 seed-languages.py omw.db

###############################################################################
# LOADING PWN CORE CONCEPTS
###############################################################################
echo
echo "Loading PWN's Core data..."
python3 load-core.py omw.db

###############################################################################

echo
echo
echo "  _____________________________________"
echo "/ OMW has been created in this folder. \\"
echo "\ Don't forget to move it to ..\\db     /"
echo " \____________________________________/"
echo "        ^__^"
echo "        (oo)\_______"
echo "        (__)\\       )\\/\\"
echo "            ||----w |"
echo "            ||     ||"
