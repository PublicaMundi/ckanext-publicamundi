#!/bin/bash

nose_opts=

dry_run=

debugger=${TEST_DEBUGGER}
test -z "${debugger}" && debugger="pdb"

[[ ! "${debugger}" =~ (i)?pdb$ ]] && echo "Unknown debugger: ${debugger}" && exit 1 

while getopts ":pnhs" opt; do
    case $opt in
        s)
            nose_opts="${nose_opts} -s"
            ;;
        n)
            dry_run="yes"
            ;;
        p)
            nose_opts="${nose_opts} --${debugger} --${debugger}-failures"
            ;;
        h)
            echo "Usage: ${0} [-p] [-s] [-n] [-h] <tests>"
            echo "    -p: Drop to pdb shell (on errors or failures)"
            echo "    -s: Print output messages from tests"
            echo "    -n: Dry run"
            echo "    -h: Print this help"
            exit 0
            ;;
        ?)
            echo "Invalid option: ${OPTARG}"
            ;;
    esac
done

shift $((OPTIND-1))

tests=${@} 
if test -z "${tests}"; then
    tests="tests" 
fi

cmd="nosetests -v --ckan --with-pylons=${TEST_INI} ${nose_opts} ${tests}"
if test -n "${dry_run}"; then
    echo 'nosetests -v --ckan --with-pylons=${TEST_INI}' ${nose_opts} ${tests}
else
    echo " * Running tests on: ${tests}"
    nosetests -v --ckan --with-pylons=${TEST_INI} ${nose_opts} ${tests}
fi
