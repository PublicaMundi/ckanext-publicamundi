import re
import zope.interface
import zope.schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from ckanext.publicamundi.lib.metadata.ibase import IObject
from ckanext.publicamundi.lib.metadata.schemata import IBaseMetadata
from ckanext.publicamundi.lib.metadata.schemata.common import *

class IFoo(IBaseMetadata):
    zope.interface.taggedValue('recurse-on-invariants', True)

    url = zope.schema.URI(
        title = u'URL',
        required = True)

    thematic_category = zope.schema.Choice(
        vocabulary = SimpleVocabulary((
            SimpleTerm('environment', 'environment', u'Environment'),
            SimpleTerm('government', 'government', u'Government'),
            SimpleTerm('health', 'health', u'Health'),
            SimpleTerm('economy', 'economy', u'Economy'))),
        title = u'Thematic category',
        required = True,
        default = 'economy')

    baz = zope.schema.TextLine(
        title = u'Baz',
        required = False,
        default = u'bazinka',
        min_length = 5)

    tags = zope.schema.List(
        title = u'Tags',
        required = False,
        value_type = zope.schema.TextLine(
            title = u'Tag',
            constraint = re.compile('[-a-z0-9]+$').match),
        max_length = 5,)

    temporal_extent = zope.schema.Object(ITemporalExtent,
        title = u'Temporal Extent',
        required = False)

    geometry = zope.schema.List(
        title = u'Geometry',
        required = False,
        value_type = zope.schema.List(
            title = u'A polygon area',
            value_type = zope.schema.Object(IPolygon,
                title = u'A polygon'
            ),
            max_length = 2),
        max_length = 2,)

    reviewed = zope.schema.Bool(
        required = False,
        title = u'Reviewed',
        description = u'This foo is reviewed by someone',)

    notes = zope.schema.Text(
        required = False,
        title = u'Notes',
        description = u'Add your notes')

    contacts = zope.schema.Dict(
        title = u'Contacts',
        required = False,
        key_type = zope.schema.Choice(
            vocabulary = SimpleVocabulary((
                SimpleTerm('personal', 'personal', u'Personal'), 
                SimpleTerm('office', 'office', u'Office'))),
            title = u'The type of contact'),
        value_type = zope.schema.Object(IContactInfo,
            title = u'Contact'))

    contact_info = zope.schema.Object(IContactInfo,
        title = u'Contact Info',
        required = True)
    
    created = zope.schema.Datetime(
        title = u'Created at',
        required = True)

    wakeup_time = zope.schema.Time(
        title = u'Wakeup time',
        required = True)

    rating = zope.schema.Int(
        title = u'Rating',
        required = True,
        min = -10,
        max = 10)
    
    grade = zope.schema.Float(
        title = u'Grade',
        required = True,
        min = -20.0,
        max = 20.0)

    password = zope.schema.Password(
        title = u'Password',
        required = False,
        min_length = 6,
    )

    @zope.interface.invariant
    def check_tag_duplicates(obj):
        s = set(obj.tags)
        if len(s) < len(obj.tags):
            raise zope.interface.Invalid('Tags contain duplicates')

