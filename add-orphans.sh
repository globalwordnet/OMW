##
## download the orphans
##
## convert to LMF
##
## read into the OMW.db
##
OMWROOT="$( cd "$( dirname "$0" )"; echo "$PWD" )"
RESDIR="$OMWROOT/omw/resources"

declare -A lngs=(\
		 ["arb"]="arb" \
	 	 ["slk"]="sk" \
	  	 ["isl"]="is" \
	  	 ["als"]="als" \
	  	 ["arb"]="arb" \
	  	 ["ell"]="el"	\
	  	 ["fra"]="fr"	\
	  	 ["heb"]="he"	\
	  	 ["hrv"]="hr"	\
		 ["lit"]="lt"	\
                )

for lng in "${!lngs[@]}"
do
    echo Processing $lng \("${lngs[$lng]}"\)
    ### fetch
    wget -nc -P ${RESDIR} http://compling.hss.ntu.edu.sg/omw/wns/${lng}.zip
    ### extract
    if [ $lng = 'lit' ]  ###
    then
	unzip -j -d ${RESDIR} ${RESDIR}/${lng}.zip slk/wn-data-${lng}.tab 
    else
	unzip -j -d ${RESDIR} ${RESDIR}/${lng}.zip ${lng}/wn-data-${lng}.tab 
    fi	   
    ### convert
    python3 scripts/tsv2lmf.py ${lng}wn "${lngs[$lng]}" scripts/ili-map.tab ${RESDIR}/wn-data-${lng}.tab >  ${RESDIR}/${lng}wn.xml
    ### validate
    xmlstarlet validate -e --dtd omw/db/WN-LMF.dtd  ${RESDIR}/${lng}wn.xml
    ### load
    
done	    
