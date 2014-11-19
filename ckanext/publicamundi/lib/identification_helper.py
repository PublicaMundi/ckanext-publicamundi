from ckanext.publicamundi.model.resource_identify import ResourceIdentify,TaskNotReady,TaskFailed,IdentifyStatus

import ckan

def identify(resource_id):
    result=_get_identification_result(resource_id)
    return result

def _get_identification_result(resource_id):
    json_result = {}
  
    res_identify_query=ckan.model.Session.query(ResourceIdentify).filter(ResourceIdentify.resource_id==resource_id)
    res_identify=res_identify_query.first()
    
    if res_identify:
	
	json_result['found'] = True
	ident_status = res_identify.get_identify_status()
	if ident_status == IdentifyStatus.NOT_PUBLISHED:
	    status,result,resource_type = get_celery_identification_result(res_identify)
	    json_result['status'] = status
	    json_result['result'] = result
	    json_result['resource_type'] = resource_type
	elif ident_status == IdentifyStatus.PUBLISHED:
	    status,resource_type = get_celery_publishing_result(res_identify)
	    json_result['status'] = status
	    json_result['resource_type'] = resource_type
	elif ident_status == IdentifyStatus.REJECTED:
	    json_result['status'] = "Rejected"
	    json_result['resource_type'] = res_identify.get_resource_type()
	return json_result
      
	
    else:
	json_result['found'] = False
	json_result['status'] = "No Action"
	return json_result

def get_celery_identification_result(res_identify_obj):
    status = None
    result = None
    resource_type = None
    try:
	status = "Identified"
	result=res_identify_obj.get_celery_task_result()
	resource_type=res_identify_obj.get_resource_type()
    except TaskNotReady:
	status = "Not Ready"
	pass
    except TaskFailed ,e:	
	status = "Identification Failed"
	pass
    
    return status,result,resource_type
  
def get_celery_publishing_result(res_identify_obj):
    status = None
    resource_type = None
    try:
	status = "Published"
	res_identify_obj.get_celery_task_result()
	resource_type=res_identify_obj.get_resource_type()
    except TaskNotReady:
	status = "Publishing"
	pass
    except TaskFailed ,e:	
	status = "Publishing Failed"
	pass
    
    return status,resource_type
	    