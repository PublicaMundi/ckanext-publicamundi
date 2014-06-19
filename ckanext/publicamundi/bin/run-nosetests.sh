#!/bin/bash

nosetests --ckan -v --with-pylons=${TEST_INI} --pdb --pdb-failures tests/
