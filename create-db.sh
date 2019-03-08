###############################################################################
# PATHS
###############################################################################

OMWROOT="$( cd "$( dirname "$0" )"; echo "$PWD" )"
BINDIR="$OMWROOT/omw/bin"
DBDIR="$OMWROOT/omw/db"
SCHEMADIR="$BINDIR"
TABDIR="$BINDIR"

CONFIG="$OMWROOT/config.py"

OMWDB="$DBDIR/omw.db"
ADMINDB="$DBDIR/admin.db"

OMWSCHEMA="$SCHEMADIR/omw.sql"
ADMINSCHEMA="$SCHEMADIR/admin.sql"

CORESYNSETS="$TABDIR/wn30-core-synsets.tab"
ILIMAP="$TABDIR/ili-map.tab"
SRELS="$TABDIR/srel.tab"
SSRELS="$TABDIR/ssrel.tab"

###############################################################################
# MAKE CONFIGURATION FILE
###############################################################################

echo
if [ -f "$CONFIG" ]; then
    echo "An OMW configuration file already exists at:"
    echo "  $CONFIG"
    echo
    echo "For security reasons, if you wish to create a new one, please delete"
    echo "this file manually and run this script again."
    echo
    echo "**NOTE** if you already have an admin database you will lose user"
    echo "access when the file is deleted! If you wish to retain access AND"
    echo "generate a new config, you must copy the SECRET_KEY setting from the"
    echo "old config file into the new one!"
    exit 1
else
    echo "Creating new configuration file at $CONFIG."

    function abspath() { readlink -f "$1"; }

    cat > "$CONFIG" <<EOF
UPLOAD_FOLDER = '${OMWROOT}/omw/public-uploads'
SECRET_KEY = $( python -c 'import os; print(repr(os.urandom(24)))' )

# ILIDB = '$( abspath "$DBDIR/ili.db" )'
OMWDB = '${OMWDB}'
ADMINDB = '${ADMINDB}'
ILI_DTD = '$( abspath "$DBDIR/WN-LMF.dtd" )'

EOF
fi

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
    echo "Creating new admin database at $ADMINDB"
    python3 "$BINDIR"/make-admin-db.py "$ADMINDB" "$ADMINSCHEMA"
    chmod go+w "$ADMINDB"
    PYTHONPATH="$OMWROOT" python3 "$BINDIR"/load-admin-users.py "$ADMINDB"
fi

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

echo
echo
echo " ___________________________________"
echo "/ The OMW and admin databases have  \\"
echo "\ been created under omw/db/        /"
echo " \_________________________________/"
echo "        ^__^"
echo "        (oo)\_______"
echo "        (__)\\       )\\/\\"
echo "            ||----w |"
echo "            ||     ||"
