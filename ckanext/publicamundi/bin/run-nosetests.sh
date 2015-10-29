#!/bin/bash

nose_opts=

log_level='INFO'

dry_run=

config=${TEST_INI}
[ ! -f "${config}" ] && config="${CKAN_PYENV}/src/ckan/test-core.ini"
echo " * Reading configuration from: ${config}"

debugger=${TEST_DEBUGGER}
[ -z "${debugger}" ] && debugger="pdb"

[[ ! "${debugger}" =~ (i)?pdb$ ]] && echo "Unknown debugger: ${debugger}" && exit 1 

while getopts ":pnhsd" opt; do
    case $opt in
        s)
            nose_opts="${nose_opts} -s"
            ;;
        n)
            dry_run="yes"
            ;;
        d)
            log_level='DEBUG'
            ;;
        p)
            nose_opts="${nose_opts} --${debugger} --${debugger}-failures"
            ;;
        h)
            echo "Usage: ${0} [-p] [-d] [-s] [-n] [-h] <tests>"
            echo "    -p: Drop to pdb shell (on errors or failures)"
            echo "    -s: Print output messages from tests"
            echo "    -n: Dry run"
            echo "    -d: Enable logging at DEBUG level (combined with '-s' option)"
            echo "    -h: Print this help"
            exit 0
            ;;
        ?)
            echo "Invalid option: ${OPTARG}"
            ;;
    esac
done

shift $((OPTIND-1))

nose_opts="--logging-level=${log_level} ${nose_opts}"

tests=${@} 
if test -z "${tests}"; then
    tests="tests" 
fi

if test -n "${dry_run}"; then
    echo "nosetests -v --ckan --with-pylons=${config} ${nose_opts} ${tests}"
else
    echo " * Running tests on: ${tests}"
    nosetests -v --ckan --with-pylons=${config} ${nose_opts} ${tests}
fi
