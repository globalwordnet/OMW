###############################################################################
# MAKE FRESH OMW.DB
###############################################################################

echo "Deleting old omw.db"
rm omw.db

echo "Creating new gwg.db"
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

echo "Loading PWN30..."
python3 load-pwn.py omw.db

###############################################################################

