
from ckanext.publicamundi.lib.metadata.fields import IField
from ckanext.publicamundi.lib.metadata import schemata
from ckanext.publicamundi.lib.metadata import (
    field_format_adapter,
    object_format_adapter,
    FieldContext, 
    IObject,
    FieldFormatter,
    ObjectFormatter)

from ckanext.publicamundi.lib.metadata.widgets import (
    markup_for_field, markup_for_object)

@field_format_adapter(IField, name='markup')
class MarkupFieldFormatter(FieldFormatter):
    
    def _format(self, value, opts):
        field = self.field
        if not field.context:
            field = field.bind(FieldContext(key=None, value=value))
        qualifier = opts.get('q')
        qual_action = 'read:%s' % (qualifier) if qualifier else 'read'
        return markup_for_field(qual_action, field, name_prefix='')

@object_format_adapter(IObject, name='markup')
class MarkupObjectFormatter(ObjectFormatter):
    
    def _format(self, obj, opts):
        qualifier = opts.get('q')
        qual_action = 'read:%s' % (qualifier) if qualifier else 'read'
        return markup_for_object(qual_action, obj, name_prefix='')


