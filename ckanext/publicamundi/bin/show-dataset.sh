#!/bin/bash

name=${1}

if test -z "${name}" ; then
    echo "Usage: ${0} <dataset-name>"
    exit 0
fi

config_file=${DEVELOPMENT_INI}

paster --plugin=ckan dataset -c ${config_file} show ${name}


