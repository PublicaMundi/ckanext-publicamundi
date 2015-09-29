import json
import os.path

from ckan.lib.base import (
    c, BaseController, render, request, abort, redirect)
import ckan.plugins.toolkit as toolkit

import ckan.new_authz as new_authz
from ckanext.publicamundi.themes.geodata.plugin import get_maps_db
#import ckanext.publicamundi.themes.geodata.mapsdb as mapsdb
#from ckanext.publicamundi.themes.geodata.plugins import get_maps_records

_ = toolkit._
NotFound = toolkit.ObjectNotFound
NotAuthorized = toolkit.NotAuthorized

FILE_PATH = '/var/local/ckan/default/ofs/storage/mapconfig.json'

class Controller(BaseController):
    def __init__(self):
        self.mapsdb = get_maps_db()
        print self.mapsdb
        #mapsdb.MapsRecords()

    def show_dashboard_maps(self):
        user_dict = self._check_access()
        #self._init_db()
        resources = self._fetch_resources()
        self._setup_template_variables(user_dict, resources)
        return render('user/dashboard_maps.html')

    #def _init_db(self):
    #    if not self.mapsdb:
    #        self.mapsdb = db.MapsRecords()

    def _fetch_resources(self):
        #if not self.maprecords:
        #    self._init_db()
        resources = self.mapsdb.get_resources()
        return resources

    def _update_resources(self, resources):
        #if not self.maprecords:
        #    self._init_db()
        return self.mapsdb.update_resources(resources)

    def _update_tree_nodes(self, nodes):
        #if not self.maprecords:
        #    self._init_db()
        return self.mapsdb.update_tree_nodes(nodes)

    def get_maps_configuration(self):
        user_dict = self._check_access()
        #self._init_db()
        if os.path.exists(FILE_PATH):
            with open(FILE_PATH, 'r') as json_data_file:
                data = json_data_file.read()
                return data
        else:
            return '[]'

    def save_maps_configuration(self):
        user_dict = self._check_access()
        #self._init_db()
        # save json config file for internal use
        config = request.params.get("json")
        if config:
            with open(FILE_PATH, 'w') as json_data_file:
                    json_data_file.write(config.encode('utf-8'))

            # and update db

            nodes = []
            resources = []
            def iter_tree(tree):
                """ Traverse tree depth-first and fill nodes, resources lists"""
                if not tree:
                    return
                data = tree.get("data")
                if data:
                    if data.get("node"):
                        nodes.append({"id": data.get("id"),
                                    "parent": data.get("parent"),
                                    "caption_en": data.get("name_en"),
                                    "caption_el": data.get("name_el"),
                                    "visible": data.get("visible"),
                                    })
                    else:
                        resources.append({"id": data.get("id"),
                                    "name_en": data.get("name_en"),
                                    "name_el": data.get("name_el"),
                                    "visible": data.get("visible"),
                                    "tree_node_caption_el": data.get("name_el"),
                                    "tree_node_caption_en": data.get("name_en"),
                                    "tree_node_id": data.get("tree_node_id"),
                                    "tree_node_index": data.get("tree_node_index"),
                                    })
                children = tree.get("children")
                if not children:
                    return
                for child in children:
                    iter_tree(child)

            print 'tree'
            tree = json.loads(config).get("config")
            iter_tree(tree)
            print 'nodes'
            print nodes
            print 'resources'
            print resources

            self._update_tree_nodes(nodes)
            self._update_resources(resources)
 
    def get_resource_fields(self):
        user_dict = self._check_access()

        resource_id = request.params.get("id")
        print 'res id'
        print resource_id

        if not resource_id:
            return

        fields = self.mapsdb.get_resource_fields(resource_id)
        print 'fields'
        print fields
        return json.dumps({'fields':fields})
        #return {'fields': json.dumps(fields)}

    def update_resource_fields(self):
        user_dict = self._check_access()

        fields = request.params.get("json")
        print 'fields to update'
        print fields
        print type(fields)
        fields = json.loads(fields).get("fields")
        print fields
        #fields = None
        #try:
        #    fields = json.loads(fields)
        #except:
        #    return
        print 'after'
        print fields

        if not fields:
            return

        self.mapsdb.update_resource_fields(fields)
        return
        #fields = self.mapsdb.get_resource_fields(resource_id)
        #print 'fields'
        #print fields
        #return json.dumps({'fields':fields})
     
    def get_tree(tree):
        if not tree.get("children"):
            return {}
        asd

    def _check_access(self):
        context, data_dict = self._get_context()
        try:
            user_dict = toolkit.get_action('user_show')(context, data_dict)
            return user_dict
        except NotFound:
            abort(404, _('User not found'))
        except NotAuthorized:
            abort(401, _('Not authorized to see this page'))

    def _get_context(self):
        context = {
            'for_view': True,
            'user': c.user or c.author,
            'auth_user_obj': c.userobj
        }
        data_dict = {'user_obj': c.userobj}
        return context, data_dict

    def _setup_template_variables(self, user_dict, resources):

        c.is_sysadmin = new_authz.is_sysadmin(c.user)
        c.user_dict = user_dict
        c.is_myself = user_dict['name'] == c.user
        c.resources = resources
