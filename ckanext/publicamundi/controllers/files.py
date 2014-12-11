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

from ckanext.publicamundi.cache_manager import get_cache
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
            up = uploader.ResourceUpload(resource={})
            filepath = up.get_path(name_or_id)
            app = fileapp.FileApp(filepath)
        elif object_type == 'source-metadata':
            up = uploader.MetadataUpload()
            filepath = up.get_path(name_or_id)
            app = fileapp.FileApp(filepath)
        elif object_type == 'metadata':
            val = get_cache('metadata').get(name_or_id)
            app = fileapp.DataApp(val, content_type='application/xml') 
        else:
            abort(404, 'Unknown object-type')
        
        # Retreive file

        try:
            status, headers, app_it = request.call_application(app)
        except:
            abort(404, 'Not Found')
        response.headers.update(dict(headers))
        response.status = status
        
        # Dump
        return app_it

    def describe_file(self, object_type, name_or_id):
        # Todo
        pass
        
    def upload_file(self, object_type):
        
        name = request.params.get('name', '') # prefix
        upload_name = name + '-upload' if name else 'upload'

        upload = request.params.get(upload_name)
        if not isinstance(upload, cgi.FieldStorage):
            abort(400, 'Expected a file upload')
        
        result = None
        if object_type == 'resources':
            abort(400, 'Cannot handle uploading of resources here')
        elif object_type == 'source-metadata':
            up = uploader.MetadataUpload(upload.filename)
            up.update_data_dict(dict(request.params), upload_name)
            up.upload(max_size=1)
        
            link = toolkit.url_for(
                controller='ckanext.publicamundi.controllers.files:Controller',
                action='download_file', 
                object_type=up.object_type,
                name_or_id=up.filename,
                filename=upload.filename)

            size = os.stat(u.filepath).st_size

            result = dict(name=u.filename, url=link, size=size)
        else:
            abort(404, 'Unknown object-type')

        response.headers['Content-Type'] = 'application/json'
        return [to_json(result)]

