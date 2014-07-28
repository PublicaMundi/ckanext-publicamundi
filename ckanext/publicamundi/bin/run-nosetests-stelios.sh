#!/bin/bash

TEST_INI=/var/local/ckan/default/pyenv/src/ckan-stelios/test-core.ini
#echo $TEST_INI
nosetests --ckan -v --with-pylons=$TEST_INI ~/ckanext-publicamundi/ckanext/publicamundi/tests/
#nosetests
