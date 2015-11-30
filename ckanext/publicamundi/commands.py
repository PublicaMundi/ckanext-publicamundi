import sys
import os
import json
import csv
import re
import itertools
import optparse
import zope.interface
import zope.schema
import logging
from optparse import make_option 
from zope.dottedname.resolve import resolve
from itertools import groupby, ifilter, islice
from operator import itemgetter, attrgetter

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
    
    >>> paster [PASTER-OPTS] publicamundi --config FILE [--setup-app] [COMMAND] [COMMAND-OPTS] [COMMAND-ARGS]

    Invoke with '?' as a COMMAND in order to get a list of available commands.
    '''

    summary = '''This is a Paster command for several publicamundi-related subcommands'''
    usage = __doc__
    group_name = 'ckanext-publicamundi'
    max_args = 15
    min_args = 0
    
    options_config = {
        'setup': (
            make_option('-n', '--dry-run', action='store_true', dest='dry_run', default=False),
        ),
        'cleanup': (
            make_option('-n', '--dry-run', action='store_true', dest='dry_run', default=False),
        ),
        'greet': (
            make_option('--name', type='string', dest='name'),
            make_option('--num', type='int', dest='num', default=5),
        ),
        'test-create-dataset': (
            make_option('--name', type='string', dest='name', default='hello-world'),
            make_option('--owner', type='string', dest='owner_org', default=None),
            make_option('--title', type='string', dest='title', default=u'Hello World'),
            make_option('--description', type='string', dest='description', default=u'Hello _World_'),
            make_option('--id', type='string', dest='identifier', default=None, 
                help='e.g. 8a728488-4453-4aef-a0f6-98d088294d5f'), 
        ),
        'import-dataset': (
            make_option('--owner', type='string', dest='owner_org', default=None),
            make_option('--dtype', type='string', dest='dtype', default='inspire'),
            make_option('--allow-rename', action='store_true', dest='allow_rename', default=False,
                help='Rename dataset if a naming conflict occurs'),
            make_option('--force', action='store_true', dest='force', default=False, 
                help='Create the dataset even if validation fails'),
        ),
        'adapter-registry-info': (
            make_option('--no-fields', action='store_false', dest='show_fields', default=True),
            make_option('--field-cls', type='string', dest='field_cls', 
                help='Filter results regarding only this field class (e.g. zope.schema.Date)'),
            make_option('--no-objects', action='store_false', dest='show_objects', default=True),
            make_option('--object-cls', type='string', dest='object_cls', 
                help='Filter results regarding only this object class'),
        ),
        'migrate-package-extra': (
            make_option('--to-str', action='store_false', dest='to_unicode', default=True),
        ),
        'import-package-translation': (
        ),
        'export-package-translation': (
            make_option('--output', type=str, dest='outfile', default='package_translations.csv'),
        ),
    }
    
    def _fake_request_context(self):
        '''Create a minimal (fake) web context for this command.

        This is commonly needed e.g. for toolkit.render() to work as it references several 
        Pylons context (thread-local) objects.
        '''

        import pylons
        from pylons.util import AttribSafeContextObj
        
        req1 = AttribSafeContextObj()
        self.registry.register(pylons.request, req1)
        pylons.request.environ = dict()
        pylons.request.params = dict()

        res1 = AttribSafeContextObj()
        self.registry.register(pylons.response, res1)
        pylons.response.headers = dict()

        ses1 = AttribSafeContextObj()
        self.registry.register(pylons.session, ses1)

        url1 = AttribSafeContextObj()
        self.registry.register(pylons.url, url1)

        self.logger.debug('Created a fake request context for Pylons')
        return

    # Subcommands
    
    @subcommand('setup', options=options_config['setup'])
    def setup_extension(self, opts, *args):    
        '''Setup publicamundi extension (create tables, populate with initial data).
        '''
        
        import ckan.model.meta as meta
        import ckanext.publicamundi.model as publicamundi_model

        if opts.dry_run:
            self.logger.info(' ** DRY-RUN ** ')
            self.logger.info('Creating tables at %s@%s: \n%s' % (
                meta.engine.url.database,
                meta.engine.url.host,
                ', '.join(publicamundi_model.Base.metadata.tables.keys())))
        else:
            publicamundi_model.Base.metadata.create_all(bind=meta.engine)
            publicamundi_model.post_setup(engine=meta.engine)

        self.logger.info('Setup complete')
    
    @subcommand('cleanup', options=options_config['cleanup'])
    def cleanup_extension(self, opts, *args):    
        '''Cleanup publicamundi extension.
        '''
        
        import ckan.model.meta as meta
        import ckanext.publicamundi.model as publicamundi_model

        if opts.dry_run:
            self.logger.info(' ** DRY-RUN ** ')
            self.logger.info('Dropping tables at %s@%s: \n%s' % (
                meta.engine.url.database,
                meta.engine.url.host,
                ', '.join(publicamundi_model.Base.metadata.tables.keys())))
        else:
            publicamundi_model.pre_cleanup(engine=meta.engine)
            publicamundi_model.Base.metadata.drop_all(bind=meta.engine)

        self.logger.info('Cleanup complete')
   
    @subcommand('greet', options=options_config['greet'])
    def greet(self, opts, *args):
        '''Greet with a helloworld message
        '''
        self.logger.info('Running "greet" with args: %r %r', opts, args)
        print 'Hello %s' %(opts.name)
    
    @subcommand('test-create-dataset', options=options_config['test-create-dataset'])
    def test_create_dataset(self, opts, *args):
        '''An example that creates a dataset using the action api.
        '''
       
        self._fake_request_context()
        
        # Create a context for action api calls
        context = {
            'model': model,
            'session': model.Session,
            'user': self.site_user.get('name'),
            'ignore_auth': True,
            'api_version': '3',
            'allow_partial_update': False
        }
        
        # Decide how to handle package identifiers
        if opts.identifier:
            # Create a dataset reusing an existing UUID
            # Note Override the catalog-wide schema inside this context
            from ckan.lib.plugins import lookup_package_plugin
            sch1 = lookup_package_plugin().create_package_schema()
            sch1['id'] = [unicode]
            context['schema'] = sch1
        else:
            # Generate a new UUID; use package_create's default behavior
            pass
        
        # Create an api request body
        pkg_dict = {
            'title': opts.title,
            'name': opts.name,
            'notes': opts.description,
            'license_id': 'cc-zero',
            'dataset_type': u'inspire',
            'owner_org': opts.owner_org,
            'inspire': {
                'title': opts.title,
                'abstract': opts.description,
                'topic_category': ["economy"],
            }
        }

        # If reusing an identifier, add the relevant keys
        if opts.identifier:
            pkg_dict['id'] = opts.identifier
            pkg_dict['inspire']['identifier'] = opts.identifier
        
        # Perform action
        pkg = get_action('package_create')(context, pkg_dict);
        print 'Created dataset with: id=%(id)s name=%(name)s:' %(pkg)
       
    @subcommand('import-dataset', options=options_config['import-dataset'])
    def import_dataset(self, opts, *args):
        '''Import a dataset from XML metadata
        '''
        if not args:
            raise ValueError('Expected an input file')
        
        source_path = os.path.realpath(args[0])
        if not os.access(source_path, os.R_OK):
            raise ValueError('The input (%s) is not a readable file' %(args[0]))
        self.logger.info('Reading XML metadata from %s' %(source_path))
   
        # Provide a request context for templating to function
        self._fake_request_context()
        
        # Create a context for action api calls
        context = {
            'model': model,
            'session': model.Session,
            'user': self.site_user.get('name'),
            'ignore_auth': True,
            'api_version': '3',
        }
        
        # Perform api request
        with open(source_path, 'r') as source:
            data_dict = {
                'source': source,
                'dtype': opts.dtype,
                'owner_org': opts.owner_org,
                'rename_if_conflict': opts.allow_rename,
                'continue_on_errors': opts.force,
            }
            result = get_action('dataset_import')(context, data_dict)
        
        self.logger.info('Imported dataset %(id)s (%(name)s)' %(result))
        return
    
    @subcommand('formatter-info', options=options_config['adapter-registry-info'])
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

    @subcommand('widget-info', options=options_config['adapter-registry-info'])
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

    @subcommand('export-package-translation',
        options=options_config['export-package-translation'])
    def export_package_translation(self, opts, *args):
        '''Export (key-based) package translations to a CSV file.
        '''
        from ckanext.publicamundi.model import PackageTranslation       
        
        outfile = opts.outfile
        if os.path.isfile(outfile):
            raise ValueError('The output (%s) allready exists' % outfile)
        
        n = 0
        q = model.Session.query(PackageTranslation)
        with open(outfile, 'w') as ofp:
            for r in q.all():
                n += 1
                t = (
                    str(r.package_id),
                    str(r.source_language),
                    str(r.language),
                    str(r.key),
                    '"' + re.sub('["]', '\\"', r.value.encode('utf-8')) + '"',
                    str(r.state)
                )
                ofp.write(','.join(t) + '\n');
            ofp.close()
        self.logger.info('Exported %d package translations for fields', n)
    
    @subcommand('import-package-translation',
        options=options_config['import-package-translation'])
    def import_package_translation(self, opts, *args):
        '''Import (key-based) package translations from a CSV file.
        
        Note that the importer will only add/update translations for existing packages. 
        
        The CSV input is expected to contain lines of: 
        (package_id, source_language, language, key, value, state)
        '''
        from ckan.plugins import toolkit
        
        from ckanext.publicamundi.lib.languages import Language
        from ckanext.publicamundi.lib.metadata.i18n import package_translation
        from ckanext.publicamundi.lib.metadata import fields, bound_field
        
        infile = args[0]
        if not os.access(infile, os.R_OK):
            raise ValueError('The input (%s) is not readable', infile)
        
        def get_package(pkg_id):
            context = {
                'model': model,
                'session': model.Session,
                'ignore_auth': True,
                'api_version': '3',
                'validate': False,
                'translate': False,
            }
            return toolkit.get_action('package_show')(context, {'id': pkg_id})

        uf = fields.TextField()
        cnt_processed_packages, cnt_skipped_packages = 0, 0
        with open(infile, 'r') as ifp:
            reader = csv.DictReader(ifp)
            for pkg_id, records in groupby(reader, itemgetter('package_id')):
                try:
                    pkg = get_package(pkg_id)
                except toolkit.ObjectNotFound:
                    pkg = None
                if not pkg:
                    cnt_skipped_packages += 1
                    continue
                cnt_processed_packages += 1
                cnt_failed_fields, cnt_updated_fields = 0, 0;
                for r in records:
                    tr = package_translation.FieldTranslation(pkg_id, r['source_language'])
                    yf = bound_field(uf, r['key'], '')
                    try:
                        tr.translate(yf, r['language'], r['value'].decode('utf-8'))
                    except Exception as ex:
                        cnt_failed_fields += 1
                        self.logger.warn('Failed to update key "%s" for package %s: %s', 
                            r['key'], pkg_id, str(ex))
                    else:    
                        cnt_updated_fields += 1
                self.logger.info('Updated translations for %d fields for package: %s', 
                    cnt_updated_fields, pkg_id)

        self.logger.info(
            'Imported translations for %d packages. Skipped %d non-existing packages',
            cnt_processed_packages, cnt_skipped_packages);
        return
    
    @subcommand('migrate-package-extra', options=options_config['migrate-package-extra'])
    def migrate_db_to_unicode(self, opts, *args):
        '''Migrate package_extra database tables to be used with {unicode/str}-based serializers
        
        We cannot use ckan.model as we are not going to create new revisions for
        objects. So, we use reflected tables (without their vdm supplement).
        '''
     
        import pylons
        
        import sqlalchemy
        from sqlalchemy.engine import reflection
        from sqlalchemy.ext.declarative import declarative_base

        from ckanext.publicamundi.lib.metadata import dataset_types
        
        engine = sqlalchemy.create_engine(pylons.config['sqlalchemy.url'])
        session_factory = sqlalchemy.orm.sessionmaker(bind=engine)
        base = declarative_base()
        refl = reflection.Inspector.from_engine(engine)
        
        package_extra_table = sqlalchemy.Table('package_extra', base.metadata)
        refl.reflecttable(package_extra_table, None)
        PackageExtra = type('PackageExtra', (base,),
            dict(__table__=package_extra_table))
        
        package_extra_revision_table = sqlalchemy.Table('package_extra_revision', base.metadata)
        refl.reflecttable(package_extra_revision_table, None)
        PackageExtraRevision = type('PackageExtraRevision', (base,), 
            dict(__table__=package_extra_revision_table))
        
        convert = None
        if opts.to_unicode:
            convert = lambda x: str(x).decode('unicode-escape')
        else:
            convert = lambda x: x.encode('unicode-escape') 
            pass

        session = session_factory()
        for prefix in dataset_types:
            for M in (PackageExtra, PackageExtraRevision):
                q = session.query(M).filter(M.key.like(prefix + '.%'))
                self.logger.info('About to convert values for %s.* keys in %s' % (prefix, M))
                i = -1
                for i, extra in enumerate(q.all()):
                    extra.value = convert(extra.value)
                self.logger.info('Converted %d records in %s' % (i + 1, M))
        self.logger.info('Flushing %d records to database...' % (len(session.dirty)))
        session.commit()
        return

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
    
