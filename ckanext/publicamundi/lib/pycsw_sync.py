import os
import logging
import datetime
import io
import requests
from lxml import etree
from ConfigParser import SafeConfigParser

from pycsw import metadata, repository, util
import pycsw.config
import pycsw.admin

log1 = logging.getLogger(__name__)

# Note The following global vars will be initialized as soon as Pylons
# configuration is available.

site_url = None

pycsw_config = None
pycsw_context = None
pycsw_database = None
pycsw_table_name = None

def setup(config):
    '''Setup module when Pylons config is available
    '''
    
    global site_url

    site_url = config['ckan.site_url']
    
    global pycsw_config, pycsw_context, pycsw_database, pycsw_table_name
    
    pycsw_config_path = config['ckanext.publicamundi.pycsw.config']
    pycsw_config = _load_config(pycsw_config_path)
    pycsw_context = pycsw.config.StaticContext()
    pycsw_database = pycsw_config.get('repository', 'database')
    pycsw_table_name = pycsw_config.get('repository', 'table')
    
    log1.info('Initialized globals from config')
    
    return

def create_record(ckan_id):
    '''Attempts to create a new CSW record for a newly created dataset.
    
    Returns None on failure, or a metadata record object on success.
    '''
    
    repo = repository.Repository(
        pycsw_database, pycsw_context, table=pycsw_table_name)
    
    record = get_record(pycsw_context, repo, site_url, ckan_id)
    if not record:
        log1.error('Cannot parse %s as a record. Skipped.' % (ckan_id))
        return None
    
    try:
        repo.insert(record, 'local', util.get_today_and_now())
        log1.info('Created record for %s' % (ckan_id))
    except Exception, err:
        log1.error('Failed to create %s: %s' % (ckan_id, err))
        return None
    
    return record

def update_record(ckan_id):
    '''Attempts to update a CSW record for a just updated dataset.
    
    Returns None on failure, or a metadata record object on success.
    '''
    
    repo = repository.Repository(
        pycsw_database, pycsw_context, table=pycsw_table_name)
    
    record = get_record(pycsw_context, repo, site_url, ckan_id)
    if not record:
        log1.error('Cannot parse %s as a record. Skipped.' % (ckan_id))
        return None
    
    update_dict = dict([(getattr(repo.dataset, key), getattr(record, key)) \
        for key in record.__dict__.keys() if key != '_sa_instance_state'])
    
    try:
        repo.session.begin()
        repo.session.query(repo.dataset).filter_by(
            ckan_id=ckan_id).update(update_dict)
        repo.session.commit()
        log1.info('Updated record for %s.' % (ckan_id))
    except Exception, err:
        repo.session.rollback()
        log1.error('Failed to update %s: %s' % (ckan_id, err))
        return None

    return record

def get_record(pycsw_context, repo, site_url, ckan_id):
    '''Build and return a metadata record from a dataset's XML dump.
    
    Returns None on failure, or a loaded metadata record on success.
    '''

    api_url = site_url.rstrip('/') + (
        '/api/publicamundi/dataset/export/%s' % (ckan_id))
    response = requests.get(api_url)

    try:
        xml = etree.parse(io.BytesIO(response.content))
    except Exception, err:
        log1.error('Could not parse XML for dataset %s: %s' % (ckan_id, err))
        return None

    try:
        record = metadata.parse_record(pycsw_context, xml, repo)[0]
    except Exception, err:
        log1.error(
            'Could not extract metadata for %s: %s' % (ckan_id, err))
        return None

    if not record.identifier:
        record.identifier = ckan_id

    return record

def _load_config(file_path):
    '''Load pyCSW configuration
    '''
    
    abs_path = os.path.abspath(file_path)
    if not os.path.exists(abs_path):
        raise ValueError('pycsw config file %s does not exist.' %(abs_path))
    
    config = SafeConfigParser()
    config.read(abs_path)
    
    log1.info('Read pyCSW config from %s' %(file_path))
    return config

