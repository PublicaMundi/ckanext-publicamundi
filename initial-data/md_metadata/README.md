Inspire Validation using OWSLib
===============================

Installation steps
------------------

1. Create virtualenv:
    
    $ virtualenv owslib_test

    $ cd owslib_test
    
    $ . ./bin/activate

2. Clone modified OWSLib:

    $ mkdir src

    $ cd src
    
    $ git clone https://github.com/geopython/OWSLib.git owslib
    
    $ cd owslib
    
    $ python setup.py build
    
    $ python setup.py install
    
    $ cd ..

3. Install lxml

    $ pip install lxml

    $ pip install jinja2

4. Clone gist:

    $ git clone https://gist.github.com/e86d845f02b99067c129.git inspire_validator
    
    $ cd inspire_validator
    
    $ python inspire.py
