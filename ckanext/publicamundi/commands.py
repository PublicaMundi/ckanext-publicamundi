import sys
import re
import os.path
import json
import itertools
import optparse
import zope.interface
import zope.schema
import logging
from optparse import make_option 
from zope.dottedname.resolve import resolve

import ckan.model as model
import ckan.logic as logic
from ckan.logic import get_action, ValidationError
from ckan.lib.cli import CkanCommand

from ckanext.publicamundi.lib.metadata.fields import *
from ckanext.publicamundi.lib.metadata import adapter_registry 
from ckanext.publicamundi.lib.metadata import schemata 
from ckanext.publicamundi.lib.metadata import types
from ckanext.publicamundi.lib.cli import CommandDispatcher

subcommand = CommandDispatcher.subcommand

class Command(CommandDispatcher):
    '''This is a Paster command for several publicamundi-related subcommands
    
    >>> paster [PASTER-OPTS] publicamundi --config FILE [--setup-app] [COMMAND] [COMMAND-OPTS]

    Invoke with '?' as a COMMAND in order to get a list of available commands.
    '''

    summary = '''This is a Paster command for several publicamundi-related subcommands'''
    usage = __doc__
    group_name = 'ckanext-publicamundi'
    max_args = 15
    min_args = 0
    
    options_config = {
        'greet': [
            make_option('--name', type='string', dest='name'),
            make_option('--num', type='int', dest='num', default=5),
        ],
        'adapter-registry-info': [
            make_option('--no-fields', action='store_false', dest='show_fields', default=True),
            make_option('--field-cls', type='string', dest='field_cls', 
                help='Filter results regarding only this field class (e.g. zope.schema.Date)'),
            make_option('--no-objects', action='store_false', dest='show_objects', default=True),
            make_option('--object-cls', type='string', dest='object_cls', 
                help='Filter results regarding only this object class'),
        ], 
    }

    @subcommand(
        name='greet', options=options_config['greet'])
    def greet(self, opts, *args):
        '''Greet with a helloworld message
        '''
        self.logger.info('Running "greet" with args: %r %r', opts, args)
        print 'Hello %s' %(opts.name)
    
    @subcommand(
        name='formatter-info', options=options_config['adapter-registry-info'])
    def print_formatter_info(self, opts, *args):
        '''Print information for registered formatters
        '''
       
        from ckanext.publicamundi.lib.metadata.util import (
            iter_object_schemata, iter_field_adaptee_vectors)
        from ckanext.publicamundi.lib.metadata import formatters
        
        format_result = lambda qa, cls: '  %-22.20s %s.%s' % (
            qa, cls.__module__, cls.__name__)
    
        object_schemata = list(iter_object_schemata())
        
        # Formatters for fields

        field_cls = resolve_field_cls(opts.field_cls) if opts.field_cls else None
        
        if opts.show_fields:
            print '\n == Formatters for zope.schema-based fields == \n'
            for adaptee in iter_field_adaptee_vectors():
                if not field_cls or adaptee[0].implementedBy(field_cls): 
                    m = adapter_registry.lookupAll(adaptee, formatters.IFormatter)
                    if not m:
                        continue
                    print '[' + ', '.join([ir.__name__ for ir in adaptee]) + ']'
                    for qa, widget_cls in m:
                        print format_result(qa, widget_cls)
        
        # Formatters for objects

        object_cls = resolve_object_cls(opts.object_cls) if opts.object_cls else None
       
        if opts.show_objects:
            print '\n == Formatters for object schemata == \n'
            for iface in object_schemata:
                if not object_cls or iface.implementedBy(object_cls): 
                    adaptee = [iface]
                    m = adapter_registry.lookupAll(adaptee, formatters.IFormatter)
                    if not m:
                        continue
                    print '[' + iface.__name__ + ']'
                    for qa, widget_cls in m:
                        print format_result(qa, widget_cls)

    @subcommand(
        name='widget-info', options=options_config['adapter-registry-info'])
    def print_widget_info(self, opts, *args):
        '''Print information for registered widgets
        '''
       
        from ckanext.publicamundi.lib.metadata.util import (
            iter_object_schemata, iter_field_adaptee_vectors)
        from ckanext.publicamundi.lib.metadata import widgets
        
        format_result = lambda qa, cls: '  %-22.20s %s.%s' % (
            qa, cls.__module__, cls.__name__)

        object_schemata = list(iter_object_schemata())

        # Widgets for fields
        
        field_cls = resolve_field_cls(opts.field_cls) if opts.field_cls else None
        
        if opts.show_fields:
            print '\n == Widgets for zope.schema-based fields == \n'
            for adaptee in iter_field_adaptee_vectors():
                if not field_cls or adaptee[0].implementedBy(field_cls): 
                    m = adapter_registry.lookupAll(adaptee, widgets.IFieldWidget)
                    if not m:
                        continue
                    print '[' + ', '.join([ir.__name__ for ir in adaptee]) + ']'
                    for qa, widget_cls in m:
                        print format_result(qa, widget_cls)
        
        # Widgets for objects

        object_cls = resolve_object_cls(opts.object_cls) if opts.object_cls else None
       
        if opts.show_objects:
            print '\n == Widgets for object schemata == \n'
            for iface in object_schemata:
                if not object_cls or iface.implementedBy(object_cls): 
                    adaptee = [iface]
                    m = adapter_registry.lookupAll(adaptee, widgets.IObjectWidget)
                    if not m:
                        continue
                    print '[' + iface.__name__ + ']'
                    for qa, widget_cls in m:
                        print format_result(qa, widget_cls)
    
class Example1(CkanCommand):
    '''This is an example of a publicamundi-specific paster command:

    >>> paster [PASTER-OPTS] publicamundi-example1 --config=FILE [COMMAND-OPTS]
    '''

    summary = 'This is an example of a publicamundi-specific paster command'
    usage = __doc__
    group_name = 'ckanext-publicamundi'
    max_args = 10
    min_args = 0

    def __init__(self, name):
        CkanCommand.__init__(self, name)
        # Configure options parser
        self.parser.add_option('--group', dest='group', help='Specify target group', type=str)

    def command(self):
        self._load_config()
        self.log = logging.getLogger(__name__)

        # Create a context for action api calls
        context = {'model':model,'session':model.Session,'ignore_auth':True}
        self.admin_user = get_action('get_site_user')(context,{})
        context.update({'user': self.admin_user.get('name')})

        context['allow_partial_update'] = True

        pkg_dict = {
            'id': "8a728488-4453-4aef-a0f6-98d088294d5f",
            'notes': 'i said _hello_ to the entire world',
            'license_id': 'cc-zero',
            'music_title': u'Queen - Another one bites the dust',
            'music_genre': 'rock',
        }

        pkg = get_action('package_update') (context, pkg_dict);

        print json.dumps(pkg, indent=4)

class Setup(CkanCommand):
    '''Setup publicamundi extension (create tables, populate with initial data).
    
    >>> paster [PASTER-OPTS] publicamundi-setup --config=FILE [COMMAND-OPTS]
    '''

    summary = 'Setup publicamundi extension'
    usage = __doc__
    group_name = 'ckanext-publicamundi'
    max_args = 10
    min_args = 0

    def __init__(self, name):
        CkanCommand.__init__(self, name)

    def command(self):
        self._load_config()
        self.log = logging.getLogger(__name__)

        import ckan.model.meta as meta
        import ckanext.publicamundi.model as publicamundi_model

        publicamundi_model.Base.metadata.create_all(bind=meta.engine)

        self.log.info('Setup complete')

class Cleanup(CkanCommand):
    '''Cleanup publicamundi extension.

    >>> paster [PASTER-OPTS] publicamundi-cleanup --config=FILE [COMMAND-OPTS]
    '''

    summary = 'Cleanup publicamundi extension'
    usage = __doc__
    group_name = 'ckanext-publicamundi'
    max_args = 10
    min_args = 0

    def __init__(self, name):
        CkanCommand.__init__(self, name)

    def command(self):
        self._load_config()
        self.log = logging.getLogger(__name__)

        import ckan.model.meta as meta
        import ckanext.publicamundi.model as publicamundi_model

        publicamundi_model.Base.metadata.drop_all(bind=meta.engine)

        self.log.info('Cleanup complete')

#
# Helpers
#

def resolve_field_cls(name):
    assert re.match('(zope|z3c)\.schema\.(\w+)$', name), (
        'The name %r doesnt look like a field class' % (name))
    field_cls = resolve(name)
    assert isinstance(field_cls, type), (
        'The name %r doesnt resolve to a class' %(name))
    assert issubclass(field_cls, zope.schema.Field), (
        'Expected a zope.schema.Field-based field class (got %r)' % (field_cls))
    return field_cls

def resolve_object_cls(name):
    object_cls = resolve(name)
    assert isinstance(object_cls, type), (
        'The name %r doesnt resolve to a class' %(name))
    assert issubclass(object_cls, types.Object), (
        'Expected a subclass of %r (got %r)' % (types.Object, field_cls))
    return object_cls
    
