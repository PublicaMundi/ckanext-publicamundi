from sqlalchemy import Table, Column, String

from ckan.model import Session

import celery as _celery
from ckan.lib.celery_app import celery

from ckanext.publicamundi.model import Base

class TaskNotReady(Exception):
    pass

class TaskFailed(Exception):
    pass

class ResourceIdentify(Base):
    __tablename__ = 'resource_identification'
    celery_task_id =  Column('resource_id', String(64), primary_key=True)
    resource_id = Column('celery_task_id', String(64))
    
    def __init__(self, celery_task_id , resource_id):
	
        self.celery_task_id = celery_task_id
        self.resource_id = resource_id
	    
        
    def get_task_result(self):
	result = celery.AsyncResult(self.celery_task_id)
	
	if result.state == _celery.states.SUCCESS:
	    return result.get()
	elif result.state == _celery.states.PENDING or result.state == _celery.states.RECEIVED:
	    raise TaskNotReady
	elif result.state == _celery.states.FAILURE:
	    raise TaskFailed()



