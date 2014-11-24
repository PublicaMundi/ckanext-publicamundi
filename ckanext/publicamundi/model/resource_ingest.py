from sqlalchemy import Table, Column, String

from ckanext.publicamundi.model import Base


class IngestStatus:
    NOT_PUBLISHED = 'not-published'
    REJECTED = 'rejected'
    PUBLISHED = 'published'

class ResourceStorerType:
    VECTOR = 'vector'
    RASTER = 'raster'

class TaskNotReady(Exception):
    pass

class TaskFailed(Exception):
    pass

class ResourceIngest(Base):
    __tablename__ = 'resource_ingest'
    resource_id = Column('resource_id', String(64), primary_key=True)
    celery_task_id = Column('celery_task_id', String(64))
    status = Column('status', String(32))
    storer_type = Column('storer_type', String(16))

    def __init__(
            self,
            celery_task_id,
            resource_id,
            storer_type,
            status=IngestStatus.NOT_PUBLISHED):

        self.celery_task_id = celery_task_id
        self.resource_id = resource_id
        self.status = status
        self.storer_type = storer_type

    def get_celery_task_result(self):
        '''Fetch task result if available, or raise a proper exception.
        '''

        import celery as _celery
        from ckan.lib.celery_app import celery

        result = celery.AsyncResult(self.celery_task_id)
        if result.state == _celery.states.SUCCESS:
            return result.get()
        elif (result.state == _celery.states.PENDING or
              result.state == _celery.states.RECEIVED):
            raise TaskNotReady()
        elif result.state == _celery.states.FAILURE:
            raise TaskFailed()
        return None

