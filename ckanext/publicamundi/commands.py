import sys
import re
import os.path
import json
import logging
import optparse
from optparse import make_option 

import ckan.model as model
import ckan.logic as logic

from ckan.logic import get_action, ValidationError
from ckan.lib.cli import CkanCommand

from ckanext.publicamundi.lib.cli import CommandDispatcher

class Command(CommandDispatcher):
    '''This is a Paster command for several publicamundi-related subcommands
    Invoke as below:
    
    paster [PASTER-OPTIONS] publicamundi [--config INI_FILE] [--setup-app] [COMMAND] [COMMAND-OPTIONS]
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
      
        from ckanext.publicamundi.lib.metadata import adapter_registry 
        from ckanext.publicamundi.lib.metadata import schemata
        from ckanext.publicamundi.lib.metadata import types
        from ckanext.publicamundi.lib.metadata import widgets
        
        print
        print ' == Widgets for zope.schema-based fields == '
        print
        for name in dir(zope.schema.interfaces):
            x = getattr(zope.schema.interfaces, name)
            if isinstance(x, zope.interface.interface.InterfaceClass):
                field_iface = x
                print field_iface.__name__
                r = adapter_registry.lookupAll(
                    [field_iface, zope.interface.Interface], widgets.IFieldWidget)
                if not r:
                    print '  --'
                for qualified_action, widget_cls in r:
                    print '  %-15.15s %s' %(qualified_action, widget_cls)

        print
        print ' == Widgets for object schemata == '
        print
        for name in dir(schemata):
            x = getattr(schemata, name)
            if isinstance(x, zope.interface.interface.InterfaceClass):
                object_iface = x
                print object_iface.__name__
                r = adapter_registry.lookupAll(
                    [object_iface, zope.interface.Interface], widgets.IObjectWidget)
                if not r:
                    print '  --'
                for qualified_action, widget_cls in r:
                    print '  %-15.15s %s' %(qualified_action, widget_cls)

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

