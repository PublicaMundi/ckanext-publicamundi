#!/bin/bash

paster_command="paster --plugin=ckan"

config_file=${DEVELOPMENT_INI}

id_patt='[0-9a-fA-F]\{8\}-[0-9a-fA-F]\{4\}-[0-9a-fA-F]\{4\}-[0-9a-fA-F]\{4\}-[0-9a-fA-F]\{12\}'

${paster_command} dataset -c ${config_file} list 2>/dev/null| grep -e "${id_patt}"


