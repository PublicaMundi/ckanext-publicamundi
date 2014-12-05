import re
import zope.interface
import zope.schema
import zope.schema.interfaces

from ckanext.publicamundi.lib.metadata.ibase import IObject, IErrorDict
from ckanext.publicamundi.lib.metadata.fields import IField

re_action_qualifier = re.compile('^([a-z][-_~a-z0-9]+)(\.[a-z][-_~a-z0-9]*)*$')

action_field = zope.schema.Choice(('read', 'edit'), required=True)

class IQualAction(zope.interface.Interface):
    '''Represents a qualified action i.e. an action coupled with a qualifier.'''

    action = action_field

    qualifier = zope.schema.NativeString(
        required=False,
        constraint=re_action_qualifier.match)

    def parents():
        '''Return ordered list of parents for this qualified action.
        
        A parent of this object is an object representing the immediate 
        superset of qualified actions.

        e.g. 
          "edit:foo" is the parent of "edit:foo.baz"
          "edit"     is the parent of "edit:foo"   
        '''
   
    def make_child(child_qualifier):
        '''Return a new object representing a child (more specialized) version
        for this qualified action.
        '''

    def to_string():
        '''Return a string representation of this qualified action.'''

    def from_string(q):
        '''Parse from a string and return a new object.'''

class ILookupContext(zope.interface.Interface):
    '''Represents a context under which a widget adapts to an object/field.'''
    
    requested_action = zope.schema.Object(IQualAction, required=True)
    
    provided_action = zope.schema.Object(IQualAction, required=True)

class IWidget(zope.interface.Interface):
    '''The interface for a generic widget'''

    action = action_field

    context = zope.schema.Object(ILookupContext, required=False)

    errors = zope.schema.Object(IErrorDict, required=False)

    def get_template():
        '''Return a filename for a template'''

    def prepare_template_vars(data):
        '''Prepare and return context data before rendering the widget'''

    def render(data):
        '''Generate markup'''

class IFieldWidget(IWidget):
    '''The interface for a widget adapter for a zope.schema-based field'''
    
    field = zope.schema.Object(IField, required=True)

    def prepare_template_vars(name_prefix, data):
        '''Prepare context before rendering the widget'''

    def render(name_prefix, data):
        '''Generate markup'''

class IObjectWidget(IWidget):
    '''The interface for a widget adapter for a IObject-based object'''
    
    obj = zope.schema.Object(IObject, required=True)

    def prepare_template_vars(name_prefix, data):
        '''Prepare context before rendering the widget'''

    def render(name_prefix, data):
        '''Generate markup'''

