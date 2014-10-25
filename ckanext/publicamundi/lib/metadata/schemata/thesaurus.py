import zope.interface
import zope.interface.verify
import zope.schema
from zope.schema.interfaces import IVocabularyTokenized
from zope.interface.verify import verifyObject

from ckanext.publicamundi.lib.metadata.ibase import IObject
from ckanext.publicamundi.lib.metadata.vocabularies import inspire_vocabularies

class IThesaurus(IObject):

    title = zope.schema.TextLine(title=u"Title", required = True)

    reference_date = zope.schema.Date(title=u"Date", required=True)

    date_type = zope.schema.Choice(
        title = u"Date Type",
        vocabulary = inspire_vocabularies.get_by_name('date-types').get('vocabulary'),
        required = True)

    name = zope.schema.NativeString()

    version = zope.schema.Float(title=u"Version", required = False)

    vocabulary = zope.schema.Object(IVocabularyTokenized, required=True)

    @zope.interface.invariant
    def check_vocabulary(obj):
        ''' Check that vocabulary provides an IVocabularyTokenized interface.
        Note that, this cannot be done via IObject's field-wise validators because
        target interface is not based on IObject.
        '''
        try:
            verifyObject(IVocabularyTokenized, obj.vocabulary)
        except Exception as ex:
            raise zope.interface.Invalid('Found an invalid vocabulary: %s' %(str(ex)))

class IThesaurusTerms(IObject):

    thesaurus = zope.schema.Object(IThesaurus, required=True)

    terms = zope.schema.List(
        title = u'Terms',
        value_type = zope.schema.NativeString(title=u'Term'),
        required = True,
        min_length = 1,
        max_length = 12)

    @zope.interface.invariant
    def check_terms(obj):
        unexpected = []
        vocabulary = obj.thesaurus.vocabulary
        for term in obj.terms:
            try:
                vocabulary.getTerm(term)
            except:
                unexpected.append(term)
        if unexpected:
            msg = 'The following terms dont belong to thesaurus "%(thesaurus_name)s": %(terms)s' %(dict(
                terms = ','.join(unexpected), thesaurus_name = obj.thesaurus.title))
            raise zope.interface.Invalid(msg)

