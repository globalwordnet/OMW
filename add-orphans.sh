##
## download the orphans
##
## convert to LMF
##
## read into the OMW.db
##
OMWROOT="$( cd "$( dirname "$0" )"; echo "$PWD" )"
RESDIR="$OMWROOT/omw/resources"

# Icelandic
#
# fixed the tab file in about 6 places (removed '"')
# wget -P ${RESDIR} http://compling.hss.ntu.edu.sg/omw/wns/isl.zip

# unzip -j -d ${RESDIR} ${RESDIR}/isl.zip wn-data-isl.tab 

# python3 scripts/tsv2lmf.py islwn is scripts/ili-map.tab ${RESDIR}/wn-data-isl.tab >  ${RESDIR}/islwn.xml

# xmlstarlet validate --dtd omw/db/WN-LMF.dtd omw/resources/islwn.xml

# Slovakian

wget -P ${RESDIR} http://compling.hss.ntu.edu.sg/omw/wns/slk.zip

unzip -j -d ${RESDIR} ${RESDIR}/slk.zip slk/wn-data-slk.tab 

python3 scripts/tsv2lmf.py slkwn sk scripts/ili-map.tab ${RESDIR}/wn-data-slk.tab >  ${RESDIR}/slkwn.xml

xmlstarlet validate --dtd omw/db/WN-LMF.dtd omw/resources/slkwn.xml
