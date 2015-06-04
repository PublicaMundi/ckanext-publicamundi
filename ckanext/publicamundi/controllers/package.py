import datetime
import os
import cgi
import logging

from pylons import g, config, session

from ckan.lib.base import (
    c, request, response, render, abort, redirect, BaseController)
import ckan.model as model
import ckan.plugins.toolkit as toolkit

from ckanext.publicamundi.lib import uploader
from ckanext.publicamundi.lib import actions as ext_actions
from ckanext.publicamundi.lib.metadata import dataset_types

log = logging.getLogger(__name__)

_ = toolkit._
_url = toolkit.url_for
_get_action = toolkit.get_action
_check_access = toolkit.check_access

class Controller(BaseController):
    
    def __after__(self):
        session.save()
        return
    
    def _import_metadata(self, post):
        '''Handle a submitted import_metadata form.
        Return a redirection URL.
        '''
        
        redirect_url = None
        
        #
        # Read and validate post parameters
        #

        # Note Authorization is enforced by the underlying action.
        owner_org = post.get('owner_org')
        if not owner_org:
            abort(400, 'The owner organization is not given')

        uv = {'group': owner_org}
        uv.update(request.urlvars)
        redirect_url = _url(**uv)
        
        dtype = post.get('dataset_type')
        if not dtype in dataset_types:
            abort(400, 'Unknown metadata schema')
        
        rename_if_conflict = post.get('rename', '') == 'y'
        continue_on_errors = post.get('force_create', '') == 'y'

        # Examine source (an upload or a link)
        # Todo Remember orig_metadata_source (as source_url)
        
        source_url = None
        source = post.get('source')
        source_upload = post.get('source-upload') 
        if source:
            # Assume source is provided as a URL
            source_url = source
        elif isinstance(source_upload, cgi.FieldStorage):
            # Assume source is an uploaded file
            up = uploader.MetadataUpload(source_upload.filename)
            up.update_data_dict(dict(post), 'source-upload')
            try:
                up.upload(max_size=1)
            except Exception as ex:
                log.error('Failed to save uploaded file %r: %s', 
                    source_upload.filename, ex.message)
                abort(400, 'Failed to upload file')
            source_url = _url(
                controller = 'ckanext.publicamundi.controllers.files:Controller',
                action = 'download_file',
                object_type = up.object_type,
                name_or_id = up.filename,
                filename = source_upload.filename)
            # Provide a file-like object as source
            source = source_upload.file
            source.seek(0, 0)
        else:
            # No source given
            session['error_summary'] = _(
                'No source specified: Upload or link to an XML file.')
            return redirect_url

        #
        # Invoke dataset_import action
        #
        
        context = { 
            'model': model, 
            'session': model.Session, 
            'api_version': 3 
        }
        
        data_dict = {
            'source': source,
            'owner_org': owner_org,
            'dtype': dtype,
            'rename_if_conflict': rename_if_conflict,
            'continue_on_errors': continue_on_errors,
        }

        try:
            result = _get_action('dataset_import')(context, data_dict)
        except ext_actions.InvalidParameter as ex:
            log.error('Cannot import package: invalid action parameters: %s' % (ex))
            session['error_summary'] = ex.message
        except (ext_actions.IdentifierConflict, ext_actions.NameConflict) as ex:
            log.error('Cannot import package: name/id conflict: %s' % (ex))
            session['error_summary'] = ex.message
        except toolkit.ValidationError as ex:
            # Parameters are valid, but result in an invalid package
            log.error('Cannot import package: metadata are invalid: %s' % (ex))
            session['error_summary'] = _('The given metadata are invalid.')
            session['errors'] = ex.error_dict
        except toolkit.Invalid as ex:
            # Parameters are valid, but source XML file is not parseable
            log.error('Cannot import package: source is invalid: %s' % (ex))
            session['error_summary'] = ex.error
        except AssertionError as ex:
            # Re-raise failed assertions
            raise
        except Exception as ex:
            log.error('Cannot import package (unexpected error): %s' % (ex))
            abort(400, 'Cannot import package')
        else:
            # Success: save result and redirect to success page
            session['result'] = result
        
        # Done
        return redirect_url
    
    def import_metadata(self):
        if request.method == 'POST':
            redirect_url = self._import_metadata(request.params)
            redirect(redirect_url)
        else:
            c.group_id = request.params.get('group')
            c.error_summary = session.pop('error_summary', None)
            c.errors = session.pop('errors', None)
            c.result = session.pop('result', None)
            return render('package/import_metadata.html')
    
