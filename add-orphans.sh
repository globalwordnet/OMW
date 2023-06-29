##
## download the orphans
##
## convert to LMF
##
## read into the OMW.db
##
OMWROOT="$( cd "$( dirname "$0" )"; echo "$PWD" )"
RESDIR="$OMWROOT/omw/resources"
CITATIONFILE="omw-citations.tab"
mkdir -p log

### Orphans
# declare -A lngs=(\
# 		 ["arb"]="arb" \
# 	 	 ["slk"]="sk" \
# 	  	 ["isl"]="is" \
# 	  	 ["als"]="als" \
# 	  	 ["arb"]="arb" \
# 	  	 ["ell"]="el"	\
# 	  	 ["fra"]="fr"	\
# 	  	 ["heb"]="he"	\
# 	  	 ["hrv"]="hr"	\
# 		 ["lit"]="lt"	\
#     )
### Everything
declare -A lngs=(\
		 ["als"]="als" \
			["arb"]="arb" \
			["bul"]="bg" \
			["cmn"]="zh" \
#			["qcn"]="zh_Hant" \
			["dan"]="da" \
			["ell"]="el" \
#			["eng"]="en" \
#			["fas"]="fa" \
			["fin"]="fi" \
			["fra"]="fr" \
			["heb"]="he" \
			["hrv"]="hr" \
			["isl"]="is" \
			["ita"]="it" \
			["jpn"]="jp" \
			["cat"]="ca" \
			["eus"]="eu" \
			["glg"]="gl" \
			["spa"]="es" \
			["ind"]="id" \
			["zsm"]="zsm" \
			["nld"]="nl" \
			["nno"]="nn" \
			["nob"]="nb" \
			["pol"]="pl" \
			["por"]="pt" \
			["ron"]="ro" \
			["lit"]="lt" \
			["slk"]="sk" \
			["slv"]="sl" \
			["swe"]="sv" \
			["tha"]="th" \
)

#declare -A lngs=( ["als"]="als" )

cat <<EOT > wn_config.py
config.add_project('iwn', 'Italian Wordnet', 'it')
config.add_project_version(
    'iwn', '1.0+wn',
    'http://192.168.1.81/~bond/omw1.0/iwn.xml',
    'http://opendefinition.org/licenses/odc-by/',
)
EOT

for lng in "${!lngs[@]}"
do
    echo Processing $lng \("${lngs[$lng]}"\)
    mkdir -p ${RESDIR}/${lng}
    ### fetch
    wget -nc -P ${RESDIR} http://compling.hss.ntu.edu.sg/omw/wns/${lng}.zip
    ### extract
    if [ $lng = 'lit' ]  ###
    then
	unzip -j -o -d ${RESDIR} ${RESDIR}/${lng}.zip slk/wn-data-${lng}.tab
	unzip -j -o -d ${RESDIR}/${lng} ${RESDIR}/${lng}.zip slk/citation.bib
	unzip -j -o -d ${RESDIR}/${lng} ${RESDIR}/${lng}.zip slk/README
    ### MCR
    elif [ $lng = 'cat' ] || [ $lng = 'eus' ] ||  [ $lng = 'spa' ] || [ $lng = 'glg' ]
    then
	 unzip -j -o -d ${RESDIR} ${RESDIR}/${lng}.zip mcr/wn-data-${lng}.tab
	unzip -j -o -d ${RESDIR}/${lng} ${RESDIR}/${lng}.zip mcr/citation.bib
	unzip -j -o -d ${RESDIR}/${lng} ${RESDIR}/${lng}.zip mcr/README
    elif [ $lng = 'cmn' ]  ### COW
    then
	unzip -j -o -d ${RESDIR} ${RESDIR}/${lng}.zip cow/wn-data-${lng}.tab
	unzip -j -o -d ${RESDIR}/${lng} ${RESDIR}/${lng}.zip cow/citation.bib
	unzip -j -o -d ${RESDIR}/${lng} ${RESDIR}/${lng}.zip cow/README
    elif [ $lng = 'ind' ]  || [ $lng = 'zsm' ] ### MSA
    then
	unzip -j -o -d ${RESDIR} ${RESDIR}/${lng}.zip msa/wn-data-${lng}.tab
	unzip -j -o -d ${RESDIR}/${lng} ${RESDIR}/${lng}.zip msa/citation.bib
	unzip -j -o -d ${RESDIR}/${lng} ${RESDIR}/${lng}.zip msa/README
    elif [ $lng = 'nno' ]  || [ $lng = 'nob' ] ### NOR
    then
	unzip -j -o -d ${RESDIR} ${RESDIR}/${lng}.zip nor/wn-data-${lng}.tab
	unzip -j -o -d ${RESDIR}/${lng} ${RESDIR}/${lng}.zip nor/citation.bib
	unzip -j -o -d ${RESDIR}/${lng} ${RESDIR}/${lng}.zip nor/README
    else
	unzip -j -o -d ${RESDIR} ${RESDIR}/${lng}.zip ${lng}/wn-data-${lng}.tab
	unzip -j -o -d ${RESDIR}/${lng} ${RESDIR}/${lng}.zip ${lng}/citation.bib
	unzip -j -o -d ${RESDIR}/${lng} ${RESDIR}/${lng}.zip ${lng}/README
    fi
    grep -P "${lng}\t|${lng}," ${CITATIONFILE} | cut -f2 > ${RESDIR}/${lng}/citation.rst
    ### convert
    python3 scripts/tsv2lmf.py ${lng}wn "${lngs[$lng]}" scripts/ili-map.tab ${RESDIR}/wn-data-${lng}.tab --version "1.0+omw" --citation=${RESDIR}/${lng}/citation.rst >  ${RESDIR}/${lng}/${lng}wn.xml
    ### validate
    xmlstarlet validate -e --dtd omw/db/WN-LMF.dtd  ${RESDIR}/${lng}/${lng}wn.xml
    tar --exclude=citation.rst --exclude=*~ -cf  ${RESDIR}/${lng}.tar  ${RESDIR}/${lng}/
    xz -z ${RESDIR}/${lng}.tar
    ###
    ### config files
    ###
    labelll=`grep "           label=" ${RESDIR}/${lng}wn.xml`
    labell="${labelll#           label=\"}"
    label="${labell%\" }"
    licenseee=`grep "           license=" ${RESDIR}/${lng}wn.xml`
    licensee="${licenseee#           license=\"}"
    license="${licensee%\" }"
    #echo $licenseee $licensee $license
    cat << EOT >>  wn_config.py
    
config.add_project('${lng}wn', '${label}',  '${lngs[$lng]}')
config.add_project_version(
    '${lng}wn', '1.0+wn',
    'http://192.168.1.81/~bond/omw1.0/${lang}/${lng}wn.xml',
    '${license}'
)g

EOT
    
done	    

### Second Italian Wordnet
mkdir -p ${RESDIR}/iwn
unzip -j -o -d ${RESDIR} ${RESDIR}/ita.zip iwn/wn-data-ita.tab
unzip -j -o -d ${RESDIR}/${lng} ${RESDIR}/${lng}.zip iwn/citation.bib
unzip -j -o -d ${RESDIR}/${lng} ${RESDIR}/${lng}.zip iwn/README
python3 scripts/tsv2lmf.py iwn "it" scripts/ili-map.tab ${RESDIR}/wn-data-ita.tab --version "1.0+omw" >  ${RESDIR}/iwn/iwn.xml
xmlstarlet validate -e --dtd omw/db/WN-LMF.dtd  ${RESDIR}/iwn/iwn.xml
