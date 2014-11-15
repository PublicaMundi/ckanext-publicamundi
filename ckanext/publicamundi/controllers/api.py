import logging
import json
import time
import datetime
import requests
import urlparse
from unidecode import unidecode

from pylons import g, config
from pylons.i18n import _

from ckan.lib.base import (BaseController, c, request, response, abort, redirect)
import ckan.model as model
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
from ckan.lib.munge import (munge_name, munge_title_to_name) 

from ckanext.publicamundi.lib.util import to_json
from ckanext.publicamundi.lib import uploader
from ckanext.publicamundi.lib.metadata import vocabularies
from ckanext.publicamundi.lib.metadata import (
    dataset_types, make_object, serializer_for, xml_serializer_for)

from ckanext.publicamundi.lib.metadata.xml_serializers import * # Fixme
from ckanext.publicamundi.lib.metadata.types.inspire_metadata import * # Fixme

log1 = logging.getLogger(__name__)

url_for = toolkit.url_for

content_types = {
    'json': 'application/json; charset=utf8',
    'xml': 'text/xml; charset=utf8'
}

class NameConflict(ValueError):
    pass

class BadRequest(ValueError):
    pass

class ValidationError(toolkit.ValidationError):
    pass

class Invalid(toolkit.Invalid):
    pass

class Controller(BaseController):

    # Autocomplete helpers
    
    def mimetype_autocomplete(self):
        q = request.params.get('incomplete', '')
        limit  = request.params.get('limit', 10)

        context = { 'model': model, 'session': model.Session }
        data_dict = { 'q': q, 'limit': limit }

        r = logic.get_action('mimetype_autocomplete')(context, data_dict)

        result_set = {
            'ResultSet': {
                'Result': [{'name': t } for t in r]
            }
        }

        response.headers['Content-Type'] = content_types['json']
        return [to_json(result_set)]

    # Vocabularies

    # Note: The 1st thought was to rely on CKAN's vocabulary/tag functionality.
    # But because (e.g. for INSPIRE-related thesauri) we need to distinguish 
    # between the human and the machine-friendly view of a term, we had to use
    # our own vocabularies. So, provided that we had some way to solve this,
    # the following api calls should not be needed any more.

    def vocabularies_list(self):
        response.headers['Content-Type'] = content_types['json']
        return [json.dumps(vocabularies.get_names())]

    def vocabulary_get(self, name):
        name = str(name)
        r = None
        
        vocab = vocabularies.get_by_name(name)
        if vocab:
            terms = vocab['vocabulary'].by_value
            r = {
                'date_type': vocab.get('date_type'),
                'reference_date': vocab.get('reference_date'),
                'title': vocab.get('title'),
                'name': vocab.get('name'),
                'terms': [{ 'value': k, 'title': terms[k].title } for k in terms],
            }
                
        response.headers['Content-Type'] = content_types['json']
        return [to_json(r)]

    # Import/Export metadata from/to XML
    
    @staticmethod
    def _get_action_context():
        return {
            'model': model, 
            'session': model.Session, 
            #'ignore_auth': True, 
            'api_version': 3,
        }

    def import_metadata(self):
        '''Import XML metadata from the specified source.
        '''
        
        dataset_type = request.params.get('type', 'ckan')
        source = urlparse.urlparse(request.params['source'])

        result = None
        try:
            result = self._import_metadata(source, dataset_type)
        except ValidationError as ex:
            result = { 
                'success': False, 
                'message': ex.error_summary, 
                'validationErrors': ex.error_dict,
            }
        except Invalid as ex:
            result = { 
                'success': False, 'message': ex.error 
            }
        except NameConflict as ex:
            result = {
                'success': False, 'message': ex.message 
            }
        except BadRequest as ex:
            result = { 
                'success': False, 'message': ex.message 
            }
             
        response.headers['Content-Type'] = content_types['json']
        return [to_json(result)]

    def _import_metadata(self, source, dataset_type, on_errors='continue'):
        '''Import XML metadata from source for a specific dataset-type.
        
        If metadata is invalid, we act depending on `on_errors` parameter:
          * 'continue': create an invalid dataset at "faulty" state
          * 'abort': abort, nothing is created
        '''
        
        result = { 'success': True, 'message': None }
         
        # Fetch raw XML data

        xmldata = None
        if source.netloc:
            if source.scheme in ['http', 'ftp']:
                r = requests.get(source.geturl())
                if not r.ok:
                    raise BadRequest('Cannot fetch metadata (unobtainable URL)')
                elif r.headers['content-type'] in ['application/xml', 'text/xml']:
                    xmldata = r.content
                else:
                    raise BadRequest('The given metadata does not seem to be XML')
            else:
                raise BadRequest('Cannot fetch metadata (unsupported scheme)')
        else:
            routes_mapper = config['routes.map']
            m = routes_mapper.match(source.path)
            if not m:
                raise BadRequest('Cannot understand source path')
            if (m['controller'] == 'ckanext.publicamundi.controllers.files:Controller' and
                    m['action'] == 'download_file' and
                    m.get('object_type', '') == 'source-metadata'):
                up = uploader.MetadataUpload()
                with open(up.get_path(m['name_or_id']), 'r') as r:
                    xmldata = r.read()    
            else:
                raise BadRequest('The given path doesnt map to a metadata source file')
        
        # Parse XML data as metadata of `dataset_type`
        
        obj = make_object(dataset_type)
        try:
            obj = xml_serializer_for(obj).loads(xmldata)
        except:
            # Map all parse exceptions to Invalid (even assertions!)
            raise Invalid('The given XML file is malformed')

        # Validate object
        # Note: We assume that if the object is valid and the name is unique,
        # then the dataset will be successfully created.

        errors = obj.validate(dictize_errors=True)
        # Fixme: use field mappings (#13)
        errors.pop('identifier', None) 
        
        # Create package
  
        if errors:
            err_message = _('The dataset contains invalid metadata')
            if on_errors == 'abort':
                raise ValidationError(errors, err_message)
            # Create an invalid dataset, so that a user can edit afterwards
            pkg = self._create_package(dataset_type, obj, state='invalid')
            result.update({
                'message': err_message,
                'validationErrors': errors,
            })
        else:
            pkg = self._create_package(dataset_type, obj, state='active') 
            
        # The package is created (either as "active" or "invalid"):
        # Return basic view/edit URLs
        
        id, name = pkg['id'], pkg['name']
        
        result.update({
            'id': id,
            'name': name,
            'links': {
                'dump': url_for('/api/action/package_show', id=name),
                'view': url_for('dataset_read', id=name),
                'edit': url_for('dataset_edit', id=name),
            }
        })
        
        return result
    
    # Fixme This seems to belong to BaseMetadata functionality
    def _create_package(self, dataset_type, obj, state='active'):
        '''Create a package from a metadata object (at the specified state). 
        '''
        
        context = self._get_action_context()
        
        if state == 'invalid':
            # Purposefully skip validation at this state
            context['skip_validation'] = True
        
        title = obj.title
        translit_title = unidecode(title)
        name = munge_title_to_name(translit_title) 
        notes = obj.abstract if hasattr(obj, 'abstract') else ''
        
        # Sanity checks (is name available?)
        
        try:
            pkg = self._get_package(name)
        except toolkit.ObjectNotFound:
            pass # noop: name is available
        else:
            raise NameConflict('The name %s is not available' % (name))
            
        # Create

        pkg = { 
            'state': state,
            'title': title,
            'name': name,
            'notes': notes,
            'dataset_type': dataset_type,
            #'groups': [{'name': 'environment'}],
            #'owner_org': 'pico-org',

        }
        
        pkg[dataset_type] = obj.to_dict(flat=True, opts={'serialize-keys': True})
        
        #context['allow_state_change'] = True
        context['return_id_only'] = True
        pkg_id = toolkit.get_action('package_create')(context, data_dict=pkg)
        log1.info('Created package %s' % name)
        
        #assert name == pkg['name']
        return {'id': pkg_id, 'name': name}
    
    def _get_package(self, name_or_id):
        '''Get the package dict by name or id. 
        
        Note that package_show will return an existing package regardless of its state
        (while package_list won't).
        '''
        
        context = self._get_action_context()
        
        pkg = { 'id': name_or_id }
        pkg = toolkit.get_action('package_show')(context, data_dict=pkg)
        
        return pkg

    def export_metadata(self):
        pass
   
    def export_to_type(self, id):
        rtype = request.params.get('type')
        if rtype:
            output = request.params.get('type')
        else:
            output = 'json'
        #file_output='json', name_or_id=None):
        dataset = self._show(id)
        dataset_type = dataset.get('dataset_type')
        obj = dataset.get(dataset_type)

        if output == 'xml':
            response.headers['Content-Type'] = content_types['xml']
            ser = xml_serializer_for_object(obj)
            return [ser.dumps()]
        else:
            response.headers['Content-Type'] = content_types['json']
            data = obj.to_json()
            return [data]

    # Helpers

    def _prepare_inspire_draft(self, insp):
        data = insp.to_dict(flat=1, opts={'serialize-keys': True})

        pkg_data = {}
        pkg_data['title'] = data.get('title')
        pkg_data['name'] = json_loader.munge(unidecode(data.get('title')))
        pkg_data['dataset_type'] = 'inspire'
        pkg_data['inspire'] = data
        pkg_data['state'] = 'draft'

        pkg = self._create_or_update(pkg_data)
        return pkg


    def _prepare_inspire(self, insp):
        data = insp.to_dict(flat=1, opts={'serialize-keys': True})

        pkg_data = {}
        pkg_data['title'] = data.get('title')
        pkg_data['name'] = json_loader.munge(unidecode(data.get('title')))
        pkg_data['dataset_type'] = 'inspire'
        pkg_data['inspire'] = data

        pkg = self._create_or_update(pkg_data)
        return pkg

    def _create_or_update(self, data):
        context = self._get_action_context()
        # Purposefully skip validation at this stage
        context.update({ 'skip_validation': True })
        if self._package_exists(data.get('name')):
            # Not supporting package upload from xml
            pass
        else:
            pkg = toolkit.get_action ('package_create')(context, data_dict=data)
            log1.info('Created package %s' % pkg['name'])
        return pkg

    def _show(self, name_or_id):
        return toolkit.get_action ('package_show') (self._get_action_context(), data_dict = {'id': name_or_id})

    def _package_exists(self, name_or_id):
        return  name_or_id in toolkit.get_action ('package_list')(self._get_action_context(), data_dict={})

    def _check_result_for_read(self, data, result):
        pass
