import json
import os.path

from ckan.lib.base import (
    c, BaseController, render, request, abort, redirect)
import ckan.plugins.toolkit as toolkit
import ckan.new_authz as new_authz

from ckanext.publicamundi.themes.geodata.plugin import get_maps_db

_ = toolkit._
NotFound = toolkit.ObjectNotFound
NotAuthorized = toolkit.NotAuthorized


class Controller(BaseController):
    def __init__(self):
        self.mapsdb = get_maps_db()
        self.resources = self.mapsdb.get_resources_with_packages_organizations()
        #self.resources = self.mapsdb.get_resources()

    def show_dashboard_maps(self):
        #user_dict = self._check_access()
        self._setup_template_variables({})
        return render('user/dashboard_maps.html')

    def get_maps_configuration(self):
        def new_tree_node(tree_pos, node):
            if node.get("parentRef"):
                del node["parentRef"]
            node["node"] = True
            return {
                "children": [],
                "parent": tree_pos.get("key"),
                "key": node.get("id"),
                "title": node.get("caption_en"),
                "expanded" :True,
                "folder": True,
                "data": node
                }

        def new_tree_resource(tree_pos, res):
            if res.get("packageRef"):
                del res["packageRef"]
            if res.get("queryableRef"):
                del res["queryableRef"]
            if res.get("treeNodeRef"):
                del res["treeNodeRef"]

            res["node"] = False
            return {
                "children": [],
                "parent": tree_pos.get("key"),
                "key": res.get("id"),
                "title": res.get("tree_node_caption_en"),
                "folder": False,
                "data": res
                }

        def find_tree_node_by_key(tree, key):
            if tree.get("key") == key:
                return tree
            elif not tree.get("children"):
                return None
            else:
                for child in tree.get("children"):
                    if find_tree_node_by_key(child, key):
                        return find_tree_node_by_key(child, key)

        def get_index(item):
            if item.get("data"):
                if item.get("data").get("index"):
                    return item.get("data").get("index")
                elif item.get("data").get("tree_node_index"):
                    return item.get("data").get("tree_node_index")

        #user_dict = self._check_access()
        #self._setup_template_variables({})

        source = {
                "children": [],
                "expanded": True,
                "key": "root",
                "title": "root"
                }

        tree_nodes = self.mapsdb.get_tree_nodes()
        for node in tree_nodes:
            if node.get("parent") == None:
                source.get("children").append(new_tree_node(source, node))
                #source.update({"children": sorted(source.get("children"), key=get_index)})
            else:
                xnode = find_tree_node_by_key(source, node.get("parent"))
                if xnode:
                    xnode.get("children").append(new_tree_node(xnode, node))
                    #xnode.update({"children": sorted(xnode.get("children"), key=get_index)})
                else:
                    #TODO: fix raise no text
                    raise 'oops something went wrong, tree node not found for visible node'
        for res in self.resources:
            if res.get("visible") == True:
                xnode = find_tree_node_by_key(source, res.get("tree_node_id"))
                if xnode:
                    xnode.get("children").append(new_tree_resource(xnode, res))
                    # sort to display correct index order
                    xnode.update({"children": sorted(xnode.get("children"), key=get_index)})

                else:
                    #TODO: fix raise no text
                    raise 'oops something went wrong, tree node not found for visible layer'

        if tree_nodes:
            next_tree_node_id = tree_nodes[-1].get("id")+1
        else:
            next_tree_node_id = 0

        return json.dumps({'source': source, 'tree_node_id': next_tree_node_id})

    def save_maps_configuration(self):
        user_dict = self._check_access()

        # read request parameters

        resources = request.params.get("resources")
        if not resources:
            resources = {}
        resources = json.loads(resources)

        tree_nodes = request.params.get("tree_nodes")
        if not tree_nodes:
            tree_nodes = {}
        tree_nodes = json.loads(tree_nodes)

        resources_fields = request.params.get("resources_fields")
        if not resources_fields:
            resources_fields = {}
        resources_fields = json.loads(resources_fields)

        resources_queryable = request.params.get("resources_queryable")
        if not resources_queryable:
            resources_queryable = {}
        resources_queryable = json.loads(resources_queryable)

        # transform dicts to lists
        res_list = []
        for resk, resv in resources.iteritems():
            d = resv.copy()
            d.update({"id":resk})
            if d.get("node"):
                del d["node"]
            res_list.append(d)

        node_list = []
        del_node_list = []
        for item in sorted(tree_nodes.items(), key=lambda x: x[1]):
            nodek = item[0]
            nodev = item[1]
            d = nodev.copy()
            d.update({"id":nodek})
            if d.get("node"):
                del d["node"]
            if d.get("visible") == False:
                del_node_list.append({"id":nodek})
            else:
                node_list.append(d)

        res_fields_list = []
        for resfk, resfv in resources_fields.iteritems():
            res_fields_list = res_fields_list + resfv

        res_quer_list = []
        for resqk, resqv in resources_queryable.iteritems():
            d = resqv.copy()
            d.update({"id":resqk})
            res_quer_list.append(d)

        # perform db tables deletes/updates/inserts
        self.mapsdb.delete_tree_nodes(del_node_list)
        self.mapsdb.upsert_tree_nodes(node_list)

        self.mapsdb.update_resources(res_list)
        self.mapsdb.update_resource_fields(res_fields_list)
        self.mapsdb.upsert_resource_queryable(res_quer_list)

        return

    def get_resource_queryable(self):
        #user_dict = self._check_access()

        resource_id = request.params.get("id")
        if not resource_id:
            return

        queryable = self.mapsdb.get_resource_queryable(resource_id)
        if not queryable:
            return

        fields = queryable.get('fields')
        return json.dumps({'fields':fields, 'queryable':queryable})

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

    def _setup_template_variables(self, user_dict):

        c.is_sysadmin = new_authz.is_sysadmin(c.user)
        #c.user_dict = user_dict
        #c.is_myself = user_dict['name'] == c.user
        c.resources = self.resources
