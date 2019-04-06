###############################################################################
# PATHS
###############################################################################

OMWROOT="$( cd "$( dirname "$0" )"; echo "$PWD" )"
OMWAPP="$OMWROOT/omw"
BINDIR="$OMWROOT/scripts"
DBDIR="$OMWROOT/omw/db"
TABDIR="$BINDIR"

CONFIG="$OMWROOT/config.py"

SECRETKEY=$( python3 -c 'import os; from base64 import b64encode; print(b64encode(os.urandom(16)).decode("utf-8"))' )
UPLOADDIR="$OMWROOT/omw/public-uploads"

OMWDB="$DBDIR/omw.db"
ADMINDB="$DBDIR/admin.db"
ILIDTD="$DBDIR/WN-LMF.dtd"

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

    read -p "Upload folder [$UPLOADDIR]: " inp
    [ -n "$inp" ] && { UPLOADDIR="$inp"; }
    read -p "Path to OMW database [$OMWDB]: " inp
    [ -n "$inp" ] && { OMWDB="$inp"; }
    read -p "Path to admin database [$ADMINDB]: " inp
    [ -n "$inp" ] && { ADMINDB="$inp"; }
    read -p "Path to ILI DTD [$ILIDTD]: " inp
    [ -n "$inp" ] && { ILIDTD="$inp"; }
    read -p "Secret key [$SECRETKEY]: " inp
    [ -n "$inp" ] && { SECRETKEY="$inp"; }
    cat > "$CONFIG" <<EOF
UPLOAD_FOLDER = '$( abspath "$UPLOADDIR" )'
SECRET_KEY = '${SECRETKEY}'
OMWDB = '$( abspath "$OMWDB" )'
ADMINDB = '$( abspath "$ADMINDB" )'
ILI_DTD = '$( abspath "$ILIDTD" )'

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
    FLASK_APP="$OMWAPP" flask init-admin-db
    chmod go+w "$ADMINDB"
    PYTHONPATH="$OMWROOT" python "$BINDIR"/load-admin-users.py "$ADMINDB"
fi

###############################################################################
# MAKE FRESH OMW.DB
###############################################################################

if [ -f "$OMWDB" ]; then
    echo "OMW database already exists at $OMWDB."
    rm -i "$OMWDB"
fi

# check if it exists again; if it exists, the user didn't want to delete
if [ ! -f "$OMWDB" ]; then
    echo "Creating new OMW database at $OMWDB"
    FLASK_APP="$OMWAPP" flask init-omw-db
    chmod go+w "$OMWDB"

    ###########################################################################
    # LOAD ILI DEPENDENCIES
    ###########################################################################

    # LOAD KIND TAGS
    echo "ILI: Loading kind data..."
    python "$BINDIR"/load-ili-kinds.py "$OMWDB"

    # LOAD STATUS TAGS
    echo "ILI: Loading status data..."
    python "$BINDIR"/load-ili-status.py "$OMWDB"


    ###########################################################################
    # LOAD OMW DEPENDENCIES
    ###########################################################################

    # LOAD POS TAGS
    echo "Loading POS data..."
    python "$BINDIR"/load-pos.py "$OMWDB"

    # LOAD SSRELS
    echo "Loading SSREL data..."
    python "$BINDIR"/load-ssrels.py "$OMWDB" "$SSRELS"

    # LOAD SRELS
    echo "Loading SREL data..."
    python "$BINDIR"/load-srels.py "$OMWDB" "$SRELS"


    ###########################################################################
    # LOAD PWN3.0+ILI
    ###########################################################################

    echo
    echo "Loading PWN30..."
    python "$BINDIR"/load-pwn.py "$OMWDB" "$ILIMAP"


    ###########################################################################
    # LOADING (ALL) OMW LANGUAGES
    ###########################################################################

    echo
    echo "Loading language data..."
    python "$BINDIR"/seed-languages.py "$OMWDB"

    ###########################################################################
    # Update LABELS (FOR PWN, for all languages)
    ###########################################################################

    echo
    echo "Creating PWN30 synset labels..."
    PYTHONPATH="$OMWROOT" python "$BINDIR"/update-label.py 

    ###########################################################################
    # LOADING PWN CORE CONCEPTS
    ###########################################################################

    echo
    echo "Loading PWN's Core data..."
    python "$BINDIR"/load-core.py "$OMWDB" "$CORESYNSETS" "$ILIMAP"

    ###########################################################################

fi

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
