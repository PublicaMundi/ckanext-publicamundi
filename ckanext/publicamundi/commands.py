import sys
import re
import os.path
import json
import logging
import itertools
import optparse
from optparse import make_option 
from zope.dottedname.resolve import resolve

import ckan.model as model
import ckan.logic as logic

from ckan.logic import get_action, ValidationError
from ckan.lib.cli import CkanCommand

from ckanext.publicamundi.lib.cli import CommandDispatcher

class Command(CommandDispatcher):
    '''This is a Paster command for several publicamundi-related subcommands
    >>> paster [PASTER-OPTIONS] publicamundi [--config INI_FILE] [--setup-app] [COMMAND] [COMMAND-OPTIONS]
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
        'widget-info': [
            make_option('--no-fields', action='store_false', dest='show_fields', default=True),
            make_option('--field-cls', type='string', dest='field_cls', 
                help='Filter results regarding only this field class (e.g. zope.schema.Date)'),
            make_option('--no-objects', action='store_false', dest='show_objects', default=True),
            make_option('--object-cls', type='string', dest='object_cls', 
                help='Filter results regarding only this object class'),
        ], 
    }

    @CommandDispatcher.subcommand(name='greet', options=options_config['greet'])
    def greet(self, opts, *args):
        '''Greet with a helloworld message
        '''
        self.logger.info('Running "greet" with args: %r %r', opts, args)
        print 'Hello %s' %(opts.name)
    
    @CommandDispatcher.subcommand(name='widget-info', options=options_config['widget-info'])
    def print_widget_info(self, opts, *args):
        '''Print information for registered widgets
        '''

        import zope.interface
        import zope.schema
        
        from itertools import product
      
        from ckanext.publicamundi.lib.metadata import adapter_registry 
        from ckanext.publicamundi.lib.metadata import schemata
        from ckanext.publicamundi.lib.metadata import types
        from ckanext.publicamundi.lib.metadata import widgets
       
        #
        # Widgets for fields
        #

        field_cls = None
        if opts.field_cls:
            assert re.match('zope\.schema\.(\w+)$', opts.field_cls), \
                'Expected a zope.schema.Field-based field class'
            field_cls = resolve(opts.field_cls)
            assert isinstance(field_cls, type), \
                'The name "%s" does not resolve to a class' %(opts.field_cls)
        
        container_field_ifaces = [ 
            zope.schema.interfaces.IList,
            zope.schema.interfaces.IDict,
            #zope.schema.interfaces.ITuple,
        ]

        leaf_field_ifaces = [
            zope.schema.interfaces.IBool,
            zope.schema.interfaces.IBytes,
            zope.schema.interfaces.IBytesLine,
            zope.schema.interfaces.IChoice,
            zope.schema.interfaces.IDate,
            zope.schema.interfaces.IDatetime,
            zope.schema.interfaces.IDecimal,
            zope.schema.interfaces.IDottedName,
            zope.schema.interfaces.IFloat,
            zope.schema.interfaces.IId,
            zope.schema.interfaces.IInt,
            zope.schema.interfaces.IObject,
            zope.schema.interfaces.IPassword,
            zope.schema.interfaces.ITerm,
            zope.schema.interfaces.IText,
            zope.schema.interfaces.ITextLine,
            zope.schema.interfaces.ITime,
            zope.schema.interfaces.ITimedelta,
            zope.schema.interfaces.IURI,
        ]

        if opts.show_fields:
            print
            print ' == Widgets for zope.schema-based fields == '
            print
            
            adaptee_vectors = [ (r,) for r in leaf_field_ifaces ] + \
                list(product(container_field_ifaces, leaf_field_ifaces)) + \
                list(product(container_field_ifaces, container_field_ifaces, leaf_field_ifaces));
            
            for adaptee in adaptee_vectors:
                if not field_cls or adaptee[0].implementedBy(field_cls): 
                    print '[' +  ', '.join([ ir.__name__ for ir in adaptee ]) + ']'
                    m = adapter_registry.lookupAll(adaptee, widgets.IFieldWidget)
                    if not m:
                        print '  --'
                    for qualified_action, widget_cls in m:
                        print '  %-22.22s %r' %(qualified_action, widget_cls)
        
        #
        # Widgets for objects
        #

        object_cls = None
        if opts.object_cls:
            object_cls = resolve(opts.object_cls)
            assert isinstance(object_cls, type), \
                'The name "%s" does not resolve to a class' %(opts.object_cls)
       
        def is_object_iface(x):
            if not isinstance(x, zope.interface.interface.InterfaceClass):
                return False
            if not x.extends(schemata.IObject):
                return False
            return True

        if opts.show_objects:
            print
            print ' == Widgets for object schemata == '
            print
            for name in dir(schemata):
                x = getattr(schemata, name)
                if not is_object_iface(x):
                    continue
                object_iface = x
                if not object_cls or object_iface.implementedBy(object_cls): 
                    print '[' + object_iface.__name__ + ']'
                    adaptee = [object_iface]
                    m = adapter_registry.lookupAll(adaptee, widgets.IObjectWidget)
                    if not m:
                        print '  --'
                    for qualified_action, widget_cls in m:
                        print '  %-22.22s %r' %(qualified_action, widget_cls)

class Example1(CkanCommand):
    '''This is an example of a publicamundi-specific paster command:
    >>> paster [PASTER-OPTIONS] publicamundi-example1 --config=../ckan/development.ini [COMMAND-OPTIONS]
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
    >>> paster [PASTER-OPTIONS] publicamundi-setup --config=../ckan/development.ini [COMMAND-OPTIONS]
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
    >>> paster [PASTER-OPTIONS] publicamundi-cleanup --config=../ckan/development.ini [COMMAND-OPTIONS]
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

