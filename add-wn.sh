#!/bin/bash
# File: add-wn.sh

if  [[ -z $VIRTUAL_ENV ]]
then
    source ./py3env/bin/activate
fi
echo
echo Using Virtual Environment ${VIRTUAL_ENV}
echo

CWD=$( cd `dirname "$0"` && pwd )
export PYTHONPATH="$CWD"


python3 scripts/validate-wn.py "$@"

