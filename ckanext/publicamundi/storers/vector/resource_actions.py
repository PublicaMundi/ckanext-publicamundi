import ckan.lib.helpers as h
from ckan.lib.dictization.model_dictize import resource_dictize
from ckan.logic import get_action
from ckan.lib.celery_app import celery
from ckan.model.types import make_uuid
from ckan import model, logic
from ckan.lib.base import abort
from ckan.common import _
import json
import ckan
from pylons import config
from ckanext.publicamundi.storers.vector import settings
from ckanext.publicamundi.model.resource_identify import ResourceIdentify,ResourceTypes,IdentifyStatus

def _get_site_url():
    try:
        return h.url_for_static('/', qualified=True)
    except AttributeError:
        return config.get('ckan.site_url', '')


def _get_site_user():
    user = get_action('get_site_user')({'model': model,
     'ignore_auth': True,
     'defer_commit': True}, {})
    return user


def identify_resource(resource_dict):
    user_api_key =  _get_site_user()['apikey']
    #res_dict = resource_dictize(resource_obj, {'model': model})
    #resource=resource_obj.as_dict()
    
    #'''With resource_dictize we get the correct resource url even if dataset is in draft state   '''
    
    #resource['url']=res_dict['url']
    task_id = make_uuid()

    data = json.dumps(resource_dict)
    celery.send_task('vectorstorer.identify', args=[data,user_api_key], task_id=task_id)
    
    #This is used when a user had rejected the injection workflow and wants to identify again the resource
    res_identify=ckan.model.Session.query(ResourceIdentify).filter(ResourceIdentify.resource_id==resource_dict['id']).first()
    if res_identify:
	ckan.model.Session.delete(res_identify)
	new_res_identify = ResourceIdentify(task_id,resource_dict['id'],ResourceTypes.VECTOR)
	ckan.model.Session.add(new_res_identify)
	ckan.model.Session.commit()
    else:
	new_res_identify = ResourceIdentify(task_id,resource_dict['id'],ResourceTypes.VECTOR)
	ckan.model.Session.add(new_res_identify)
    
    
def _get_geoserver_context():
    geoserver_context = json.dumps({'geoserver_url': config['ckanext-vectorstorer.geoserver_url'],
     'geoserver_workspace': config['ckanext-vectorstorer.geoserver_workspace'],
     'geoserver_admin': config['ckanext-vectorstorer.geoserver_admin'],
     'geoserver_password': config['ckanext-vectorstorer.geoserver_password'],
     'geoserver_ckan_datastore': config['ckanext-vectorstorer.geoserver_ckan_datastore']})
    return geoserver_context


def create_vector_storer_task(resource, layer_params):
    user = _get_site_user()
    resource_package_id = resource.as_dict()['package_id']
    cont = {'package_id': resource_package_id,
     'site_url': _get_site_url(),
     'apikey': user.get('apikey'),
     'site_user_apikey': user.get('apikey'),
     'user': user.get('name'),
     'db_params': config['ckan.datastore.write_url'],
     'layer_params':layer_params}
    

    context = json.dumps(cont)
    geoserver_context = _get_geoserver_context()
    data = json.dumps(resource_dictize(resource, {'model': model}))
    task_id = make_uuid()
    celery.send_task('vectorstorer.upload', args=[geoserver_context, context, data], task_id=task_id)
    
    res_identify_query=ckan.model.Session.query(ResourceIdentify).filter(ResourceIdentify.resource_id==resource.id).first()
    res_identify_query.set_identify_status(IdentifyStatus.PUBLISHED)
    res_identify_query.set_celery_task_id(task_id)
    ckan.model.Session.commit()


def update_vector_storer_task(resource):
    user = _get_site_user()
    resource_package_id = resource.as_dict()['package_id']
    resource_list_to_delete = _get_child_resources(resource.as_dict())
    context = json.dumps({'resource_list_to_delete': resource_list_to_delete,
     'package_id': resource_package_id,
     'site_url': _get_site_url(),
     'apikey': user.get('apikey'),
     'site_user_apikey': user.get('apikey'),
     'user': user.get('name'),
     'db_params': config['ckan.datastore.write_url']})
    geoserver_context = _get_geoserver_context()
    data = json.dumps(resource_dictize(resource, {'model': model}))
    task_id = make_uuid()
    celery.send_task('vectorstorer.update', args=[geoserver_context, context, data], task_id=task_id)


def delete_vector_storer_task(resource, pkg_delete = False):
    user = _get_site_user()
    data = None
    resource_list_to_delete = None
    if (resource['format'] == settings.WMS_FORMAT or resource['format'] == settings.DB_TABLE_FORMAT) and resource.has_key('vectorstorer_resource'):
        data = json.dumps(resource)
        if pkg_delete:
            resource_list_to_delete = _get_child_resources(resource)
    else:
        data = json.dumps(resource)
        resource_list_to_delete = _get_child_resources(resource)
    context = json.dumps({'resource_list_to_delete': resource_list_to_delete,
     'site_url': _get_site_url(),
     'apikey': user.get('apikey'),
     'site_user_apikey': user.get('apikey'),
     'user': user.get('name'),
     'db_params': config['ckan.datastore.write_url']})
    geoserver_context = _get_geoserver_context()
    task_id = make_uuid()
    celery.send_task('vectorstorer.delete', args=[geoserver_context, context, data], task_id=task_id)
    if resource.has_key('vectorstorer_resource') and not pkg_delete:
        _delete_child_resources(resource)


def _delete_child_resources(parent_resource):
    user = _get_site_user()
    temp_context = {'model': ckan.model,
     'user': user.get('name')}
    current_package = get_action('package_show')(temp_context, {'id': parent_resource['package_id']})
    resources = current_package['resources']
    for child_resource in resources:
        if child_resource.has_key('parent_resource_id'):
            if child_resource['parent_resource_id'] == parent_resource['id']:
                action_result = logic._actions['resource_delete'](temp_context, {'id': child_resource['id']})


def _get_child_resources(parent_resource):
    child_resources = []
    user = _get_site_user()
    temp_context = {'model': ckan.model,
     'user': user.get('name')}
    current_package = get_action('package_show')(temp_context, {'id': parent_resource['package_id']})
    resources = current_package['resources']
    for child_resource in resources:
        if child_resource.has_key('parent_resource_id'):
            if child_resource['parent_resource_id'] == parent_resource['id']:
                child_resources.append(child_resource['id'])

    return child_resources


def pkg_delete_vector_storer_task(package):
    user = _get_site_user()
    context = {'model': ckan.model,
     'session': ckan.model.Session,
     'user': user.get('name')}
    resources = package['resources']
    for res in resources:
        if res.has_key('vectorstorer_resource') and res['format'] == settings.DB_TABLE_FORMAT:
            res['package_id'] = package['id']
            delete_vector_storer_task(res, True)