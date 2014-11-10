from ckanext.publicamundi.model.resource_identify import ResourceIdentify,TaskNotReady,TaskFailed

import ckan

def identify(resource_id):
    result=_get_identification_result(resource_id)
    return result

def _get_identification_result(resource_id):
    json_result = {}
  
    res_identify_query=ckan.model.Session.query(ResourceIdentify).filter(ResourceIdentify.resource_id==resource_id)
    res_identify=res_identify_query.first()
    
    if res_identify:
	
	try:
	    json_result['success'] = True
	    result=res_identify.get_task_result()
	    
	    json_result['result'] = result
	    return json_result
	
	except TaskNotReady:
	    json_result['success'] = False
	    json_result['result'] = "Not Ready"
	    return json_result
	    pass
	except TaskFailed ,e:
 
	    json_result['success'] = False
	    json_result['result'] = "Failed"
	    return json_result
	    
    else:
	json_result['success'] = False
	json_result['result'] = "Not Found"
	return json_result