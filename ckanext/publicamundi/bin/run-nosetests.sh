#!/bin/bash

nose_opts=

log_level='WARN'

dry_run=

config=${TEST_INI}
[ ! -f "${config}" ] && config="${CKAN_PYENV}/src/ckan/test-core.ini"
echo " * Reading configuration from: ${config}"

debugger=${TEST_DEBUGGER}
[ -z "${debugger}" ] && debugger="pdb"

[[ ! "${debugger}" =~ (i)?pdb$ ]] && echo "Unknown debugger: ${debugger}" && exit 1 

while getopts ":H:pnhsvd" opt; do
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
        v)  
            log_level='INFO'
            ;;
        p)
            nose_opts="${nose_opts} --${debugger} --${debugger}-failures"
            ;;
        H) 
            nose_opts="${nose_opts} --with-html --html-file=${OPTARG}"
            ;;
        h)
            echo "Usage: ${0} [-p] [-d] [-v] [-s] [-n] [-h] [-H <outfile>] <tests>"
            echo "    -p: Drop to pdb shell (on errors or failures)"
            echo "    -s: Print output messages from tests"
            echo "    -H <outfile>: Generate HTML report into given file"
            echo "    -n: Dry run"
            echo "    -d: Enable logging at DEBUG level (combined with '-s' option)"
            echo "    -v: Enable logging at INFO level (combined with '-s' option)"
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
