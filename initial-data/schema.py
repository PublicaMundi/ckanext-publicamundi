import zope.schema
import re
import time
 
import ckanext.publicamundi.lib 
from ckanext.publicamundi.lib.metadata.ibase import IBaseObject 

class IPointΟfContact(IBaseObject):
    organizationName = zope.schema.TextLine(
        title = u"Organisation Name",
        required = True)
        
    email = zope.schema.TextLine(
        title = u"E-mail",
        required = True,
        constraint = re.compile("[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?").match)

 
class IInspireMetadata(IBaseMetadata): 
     
    zope.interface.taggedValue('recurse-on-invariants', True) 
    
    metadataPointOfContact = zope.schema.List(
        title = u'Metadata Point of Contact',
        required = True,
        value_type = zope.schema.Object(IPointΟfContact,
            title = u'A Point of Contact'),
    )
        
    metadataDate = zope.schema.DateTime(
        title = u'Metadata Date',
        required = False,
        default = time.strftime("%d-%m-%Y"),
        max = time.strftime("%d-%m-%Y")
    )
        
    metadataLanguage = zope.schema.Choice(("Bulgarian","Czech","Danish","Dutch","English","Estonian","Finnish","French","German","Greek","Hungarian","Irish","Italian","Latvian","Lithuanian","Maltese","Polish","Portuguese","Romanian","Slovak","Slovenian","Spanish","Swedish"),
        title = u'Metadata Language',
        required = True,
        default = "English")
    
 }