import ckan

from ckanext.publicamundi.model.resource_ingest import(
    ResourceIngest, TaskNotReady, TaskFailed, IngestStatus)

# Fixme: The status strings returned by the following functions should be
# drawn from an enumeration (and be transformed to human-readable messages
# at template level).

def get_result(resource_id):
    '''Provide an overall status of the resource ingestion process.

    This combines both identification and ingestion status.
    '''

    result = {}

    res_identify_query = ckan.model.Session.query(ResourceIngest).filter(
        ResourceIngest.resource_id == resource_id)
    res_identify = res_identify_query.first()

    if res_identify:
        result['found'] = True
        ingest_status = res_identify.status
        if ingest_status == IngestStatus.NOT_PUBLISHED:
            status, task_result, storer_type = get_celery_identification_result(res_identify)
            result['status'] = status
            result['result'] = task_result
            result['storer_type'] = storer_type
        elif ingest_status == IngestStatus.PUBLISHED:
            status, storer_type = get_celery_ingestion_result(res_identify)
            result['status'] = status
            result['storer_type'] = storer_type
        elif ingest_status == IngestStatus.REJECTED:
            result['status'] = "Rejected"
            result['storer_type'] = res_identify.storer_type
    else:
        result['found'] = False
        result['status'] = "No Action"
    
    return result

def get_celery_identification_result(res_identify_obj):
    status = None
    result = None
    storer_type = None
    try:
        status = "Identified"
        result = res_identify_obj.get_celery_task_result()
        storer_type = res_identify_obj.storer_type
    except TaskNotReady as ex:
        status = "Not Ready"
        pass
    except TaskFailed as ex:
        status = "Identification Failed"
        pass

    return status, result, storer_type

def get_celery_ingestion_result(res_identify_obj):
    status = None
    storer_type = None
    try:
        status = "Published"
        res_identify_obj.get_celery_task_result()
        storer_type = res_identify_obj.storer_type
    except TaskNotReady as ex:
        status = "Publishing"
        pass
    except TaskFailed as ex:
        status = "Publishing Failed"
        pass

    return status, storer_type

