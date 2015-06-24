import codecs
import json
from sqlalchemy import func, exc, and_

import ckan.model as model
from ckan.lib.base import BaseController, c, request, abort
import ckan.plugins.toolkit as toolkit

from ckanext.publicamundi.storers.vector import resource_actions
from ckanext.publicamundi.storers.vector.model.spatial_ref_sys import SpatialRefSys
from ckanext.publicamundi.storers.vector.lib.encodings import encodings

_ = toolkit._
_check_access = toolkit.check_access
_get_action = toolkit.get_action
DataError = exc.DataError


class VectorController(BaseController):
    '''Store vector data under postgis, publish at geoserver
    '''

    def _make_default_context(self):
        return {
            'model': model,
            'session': model.Session,
            'user': c.user,
        }
    
    def ingest(self, resource_id):
        
        # Check if authorized to update

        context = self._make_default_context()
        try:
            _check_access('resource_update', context, dict(id=resource_id))
        except toolkit.ObjectNotFound as ex:
            abort(404)
        except toolkit.NotAuthorized as ex:
            abort(403, _('Not authorized to update resource'))
            
        # Read layer opts, procceed to ingestion

        layer_options = json.loads(request.params.get('data'))

        resource = model.Session.query(model.Resource).get(resource_id)
        resource_actions.create_ingest_resource(resource, layer_options)
    
    def search_epsg(self):
        '''Searching on the spatial_ref_sys table to find
        results matched the query. Returns a json for autocomplte'''
        
        search_term = request.params.get('term')
       
        like_condition="%%%s%%"%(search_term.lower())
        
        results = model.Session.query(SpatialRefSys).filter(and_(
                  func.lower(SpatialRefSys.srtext).like(
                  like_condition),(SpatialRefSys.auth_name=='EPSG'))).all()
        
        autocomplete_json = []
        for res in results:
            autocomplete_json.append(res.get_autocomplete_dict())
        return json.dumps(autocomplete_json)

    
    def search_encoding(self):
        '''Searching on a list of encodings to find
        results matched the query. Returns a json for autocomplte'''
        
        search_term = request.params.get('term').lower()
        
        # Search if the term is in encoding languages
        results_lang = filter(lambda encoding: search_term in encoding['languages'].
                              lower() , encodings)
        # Search if the term is in encoding aliases
        results_alias = filter(lambda encoding: search_term in encoding['aliases'].
                              lower() , encodings)

        autocomplete_json = []
        results = results_lang + results_alias
        
        # Create a json containing the results languages and aliases search results
        for res in results:
            autocomplete_json.append(self.get_enc_autocomplete_dict(res))
        return json.dumps(autocomplete_json)
    
    def validation_check(self):
        ''' Checks if the encoding or projection (EPSG Code) a user 
        entered is vaild.'''

        valid = None
        if 'encoding' in request.params:
            valid = self._encoding_valid(request.params.get('encoding'))
        elif 'projection' in request.params:
            valid = self._epsg_valid(request.params.get('projection'))
        return json.dumps(valid)

    def get_enc_autocomplete_dict(self, encoding_dict):
        '''Returns a dictionary containing an encoding entity (used by jquery
        autocomplete).'''
        
        autocomplete_dict = {}
        aliases = encoding_dict['aliases']
        languages = encoding_dict['languages']
        codec = encoding_dict['codec']
        if len(aliases)>0:
            autocomplete_dict['label'] = languages + " : " + aliases
        else:
            autocomplete_dict['label'] = languages + " : " + codec
        autocomplete_dict['value'] = codec
        return autocomplete_dict

    def _encoding_valid(self, encoding):
        '''Checks if the encoding codec exists.'''
        encoding_result = filter(lambda _encoding: encoding.lower() == 
                                 _encoding['codec'].lower() , encodings)
        if len(encoding_result) == 0:
                return False
        else:
            return True

    def _epsg_valid(self, epsg):
        '''Checks if the epsg code exists.'''
        try:
            epsg_result = model.Session.query(SpatialRefSys).filter(
                    SpatialRefSys.auth_srid == epsg).first()
            if epsg_result is None:
                return False
            else:
                return True
        except DataError:
            return False