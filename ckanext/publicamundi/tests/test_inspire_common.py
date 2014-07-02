import zope.interface
import zope.schema
import copy
import json
import datetime
from ckanext.publicamundi.tests.helpers import test
from ckanext.publicamundi.lib.metadata.types import *
from ckanext.publicamundi.tests.fixtures import * 
##
## Responsible Party
##

def test_rp1():
    ''' Responsible Party validation errors, name, email not list'''
    test(rp1,set(['organization','email','role']))
    
def test_rp2():
    ''' Responsible Party validation errors, empty fields'''
    test(rp2,set(['email','role']))
    
def test_rp3():
    ''' Responsible Party validation errors, email not correct'''
    test(rp3,set(['email']))
    
def test_rp4():
    '''Responsible Party correct schema'''
    test(rp_correct,None)

##
## Conformity 
##

def test_cnf1():
    '''Conformity validation errors date, creation, degree'''
    test(cnf1,set(['date','date_type','degree']))

def test_cnf2():
    '''Conformity correct schema'''
    test(cnf_correct,None)

##
## Free keywords 
##

def test_fkw1():
    '''Free Keywords validation errors: originating_vocabulary,date_type'''
    test(fkw1,set(['date_type']))

def test_fkw2():
    '''Free Keywords validation invariant error - not all fields set'''
    test(fkw2,set(['__after']))

def test_fkw3():
    '''Free Keywords correct schema'''
    test(fkw_correct,None)

##
## Geographic BBox 
##

def test_gbb1():
    '''GBBox validation errors: all not float'''
    test(gbb1,set(['nblat','sblat','eblng','wblng']))

def test_gbb2():
    '''GBBox validation errors - nblat, wblng greater than max allowed'''
    test(gbb2,set(['nblat','wblng']))

def test_gbb3():
    '''GBBox correct schema'''
    test(gbb_correct,None)

##
## Temporal Extent 
##

def test_te1():
    '''Temporal Extent validation errors: start not date'''
    test(te1,set(['start']))

def test_te2():
    '''Temporal Extent invariant error - start date greater than end date'''
    test(te2,set(['__after']))

def test_te3():
    '''Temporal Extent correct schema'''
    test(te_correct,None)

##
## Spatial Resolution 
##

def test_sr1():
    '''Spatial Resolution validation error - distance not int '''
    test(sr1,set(['distance']))

def test_sr2():
    '''Spatial Resolution invariant error - not all values set'''
    test(sr2,set(['__after']))

def test_sr3():
    '''Spatial Resolution correct schema - no values set'''
    test(sr3,None)

def test_sr4():
    '''Spatial Resolution correct schema'''
    test(sr_correct,None)


## Main ##

if __name__ == '__main__':

    test_rp1();
    test_rp2();
    test_rp3();
    test_rp4();
