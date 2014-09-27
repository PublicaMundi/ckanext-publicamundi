#!/bin/bash

paster_command="paster --plugin=ckan"

config_file=${DEVELOPMENT_INI}

id_patt='[0-9a-fA-F]\{8\}-[0-9a-fA-F]\{4\}-[0-9a-fA-F]\{4\}-[0-9a-fA-F]\{4\}-[0-9a-fA-F]\{12\}'

names=$(${paster_command} dataset -c ${config_file} list| grep -e "${id_patt}"| cut -d ' ' -f 2)

for name in ${names}
do
    ${paster_command} dataset -c ${config_file} purge ${name}
done

