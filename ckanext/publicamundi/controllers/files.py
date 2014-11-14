import datetime
import os
import cgi
import logging

from paste import fileapp
from pylons import url

from ckan.lib.base import (
    c, request, response, render, abort, redirect, BaseController)
import ckan.model as model
import ckan.plugins.toolkit as toolkit

from ckanext.publicamundi.lib.util import to_json
import ckanext.publicamundi.lib.uploader as uploader

log1 = logging.getLogger(__name__)

class Controller(BaseController):
    
    def download_file(self, object_type, name_or_id, filename=None):
        '''Download file from CKAN's filestore, grouped under `object_type` and
        identified by `name_or_id` inside this group.
        '''
        
        filepath = None
        if object_type == 'resources':
            u = uploader.ResourceUpload(resource={})
            filepath = u.get_path(name_or_id)
        elif object_type == 'source-metadata':
            u = uploader.MetadataUpload()
            filepath = u.get_path(name_or_id)
        else:
            abort(404, 'Unknown object-type')
        
        # Retreive file

        app = fileapp.FileApp(filepath)
        try:
            status, headers, app_it = request.call_application(app)
        except:
            abort(404, 'Not Found')
        response.headers.update(dict(headers))
        response.status = status
        
        # Dump file

        return app_it

    def describe_file(self, object_type, name_or_id):
        pass
        
    def upload_file(self, object_type):
        
        name = request.params.get('name', '') # prefix
        upload_name = name + '-upload' if name else 'upload'

        upload = request.params.get(upload_name)
        if not isinstance(upload, cgi.FieldStorage):
            abort(400, 'Expected a file upload')
        
        result = None
        if object_type == 'resources':
            abort(400, 'Uploading of resources is not handled here!')
        elif object_type == 'source-metadata':
            u = uploader.MetadataUpload(upload.filename)
            u.update_data_dict(dict(request.params), upload_name)
            u.upload(max_size=1)
        
            l = toolkit.url_for('publicamundi-files-download-file', 
                object_type='source-metadata', name_or_id=u.filename,
                filename=upload.filename)
            n = os.stat(u.filepath).st_size

            result = dict(name=u.filename, url=l, size=n)
        else:
            abort(404, 'Unknown object-type')

        response.headers['Content-Type'] = 'application/json'
        return [to_json(result)]

