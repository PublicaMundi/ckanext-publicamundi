import zope.interface
import zope.schema
import copy
import json
import datetime

from ckanext.publicamundi.lib.metadata.base import *
from ckanext.publicamundi.lib.metadata.types import *

from ckanext.publicamundi.tests.helpers import assert_faulty_keys
from ckanext.publicamundi.tests.fixtures import * 


##
## Fixtures
##


'''
kw_gemet_concepts_correct = GemetConcepts(
        thesaurus = Thesaurus(title = u'inspire',
            reference_date = datetime.date.today(),
            date_type = 'creation'))

kw_gemet_groups_correct = GemetGroups(
        thesaurus = Thesaurus(title = u'inspire',
            reference_date = datetime.date.today(),
            date_type = 'creation'))

kw_gemet_supergroups_correct = GemetSupergroups(
        thesaurus = Thesaurus(title = u'inspire',
            reference_date = datetime.date.today(),
            date_type = 'creation'))

kw_gemet_themes_correct = GemetThemes(
        thesaurus = Thesaurus(title = u'inspire',
            reference_date = datetime.date.today(),
            date_type = 'creation'))

kw_geoss_earth_observation_correct = GeossEarthObservation(
        thesaurus = Thesaurus(title = u'inspire',
            reference_date = datetime.date.today(),
            date_type = 'creation'))

kw_geoss_societal_benefit_areas_correct = GeossSocietalBenefitAreas(
        thesaurus = Thesaurus(title = u'inspire',
            reference_date = datetime.date.today(),
            date_type = 'creation'))

kw_inspire_feature_concept_correct = InspireFeatureConcept(
        thesaurus = Thesaurus(title = u'inspire',
            reference_date = datetime.date.today(),
            date_type = 'creation'))

kw_inspire_glossary_correct = InspireGlossary(
        thesaurus = Thesaurus(title = u'inspire',
            reference_date = datetime.date.today(),
            date_type = 'creation'))
'''

def test_kw1():
    ''' INSPIRE correct '''
    assert_faulty_keys(kw_inspire_correct, [])

if __name__ == '__main__':
    #print repr(insp3)
    #print 'insp 3 ='
    #print insp3
    test_kw1()
