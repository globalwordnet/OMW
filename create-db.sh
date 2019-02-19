###############################################################################
# PATHS
###############################################################################

OMWROOT="$( cd "$( dirname "$0" )"; echo "$PWD" )"
BINDIR="$OMWROOT/omw/bin"
DBDIR="$OMWROOT/omw/db"
SCHEMADIR="$BINDIR"
TABDIR="$BINDIR"

OMWDB="$DBDIR/omw.db"
ADMINDB="$DBDIR/admin.db"

OMWSCHEMA="$SCHEMADIR/omw.sql"
ADMINSCHEMA="$SCHEMADIR/admin.sql"

CORESYNSETS="$TABDIR/wn30-core-synsets.tab"
ILIMAP="$TABDIR/ili-map.tab"
SRELS="$TABDIR/srel.tab"
SSRELS="$TABDIR/ssrel.tab"


###############################################################################
# MAKE FRESH OMW.DB
###############################################################################

if [ -f "$OMWDB" ]; then
    echo "OMW database already exists at $OMWDB."
    rm -i "$OMWDB"
fi

echo "Creating new OMW database at $OMWDB"
python3 "$BINDIR"/make-omw-db.py "$OMWDB" "$OMWSCHEMA"
chmod go+w "$OMWDB"

###############################################################################
# LOAD ILI DEPENDENCIES
###############################################################################

# LOAD KIND TAGS
echo "ILI: Loading kind data..."
python3 "$BINDIR"/load-ili-kinds.py "$OMWDB"

# LOAD STATUS TAGS
echo "ILI: Loading status data..."
python3 "$BINDIR"/load-ili-status.py "$OMWDB"


###############################################################################
# LOAD OMW DEPENDENCIES
###############################################################################

# LOAD POS TAGS
echo "Loading POS data..."
python3 "$BINDIR"/load-pos.py "$OMWDB"

# LOAD SSRELS
echo "Loading SSREL data..."
python3 "$BINDIR"/load-ssrels.py "$OMWDB" "$SSRELS"

# LOAD SRELS
echo "Loading SREL data..."
python3 "$BINDIR"/load-srels.py "$OMWDB" "$SRELS"


###############################################################################
# LOAD PWN3.0+ILI
###############################################################################
echo
echo "Loading PWN30..."
python3 "$BINDIR"/load-pwn.py "$OMWDB" "$ILIMAP"


###############################################################################
# LOAD/UPDATE PWN FREQUENCIES
###############################################################################
echo
echo
echo "Loading PWN30 frequencies..."
python3 "$BINDIR"/load-pwn-freq.py "$OMWDB"
echo "Updating (all) frequencies..."
python3 "$BINDIR"/update-freq.py "$OMWDB"


###############################################################################
# Update LABELS (FOR PWN)
###############################################################################
echo
echo "Loading PWN30 synset labels..."
python3 "$BINDIR"/update-label.py "$OMWDB"


###############################################################################
# LOADING (ALL) OMW LANGUAGES
###############################################################################
echo
echo "Loading language data..."
python3 "$BINDIR"/seed-languages.py "$OMWDB"

###############################################################################
# LOADING PWN CORE CONCEPTS
###############################################################################
echo
echo "Loading PWN's Core data..."
python3 "$BINDIR"/load-core.py "$OMWDB" "$CORESYNSETS" "$ILIMAP"

###############################################################################
# MAKE ADMIN DATABASE
###############################################################################
echo
if [ -f "$ADMINDB" ]; then
    echo "admin database already exists at $ADMINDB."
    rm -i "$ADMINDB"
fi

# check if it exists again; if it exists, the user didn't want to delete
if [ ! -f "$ADMINDB" ]; then
    echo "Creating new admin database at $ADMIN"
    python3 "$BINDIR"/make-admin-db.py "$ADMINDB" "$ADMINSCHEMA"
    chmod go+w "$ADMINDB"
    python3 "$BINDIR"/load-admin-users.py "$ADMINDB"
fi

###############################################################################

echo
echo
echo "  __________________________________"
echo "/ The OMW and admin databases have \\"
echo "\ been created under omw/db/        /"
echo " \_________________________________/"
echo "        ^__^"
echo "        (oo)\_______"
echo "        (__)\\       )\\/\\"
echo "            ||----w |"
echo "            ||     ||"
