import os
import logging
import datetime
from lxml import etree
from ConfigParser import SafeConfigParser

import pycsw
import pycsw.config
import pycsw.admin

import ckan.model as model
import ckan.plugins.toolkit as toolkit

from ckanext.publicamundi.lib.metadata import (
    make_metadata_object, xml_serializer_for)

log1 = logging.getLogger(__name__)

# Note The following global vars will be initialized as soon as Pylons
# configuration is available.

site_url = None

pycsw_config = None
pycsw_context = None
pycsw_database = None
pycsw_table_name = None

_repo = None

def setup(ckan_site_url, pycsw_config_file):
    '''Setup module when Pylons config is available
    '''
    
    global site_url

    site_url = ckan_site_url.rstrip('/')
    
    global pycsw_config, pycsw_context, pycsw_database, pycsw_table_name
    
    pycsw_config = _load_config(pycsw_config_file)
    pycsw_context = pycsw.config.StaticContext()
    pycsw_database = pycsw_config.get('repository', 'database')
    pycsw_table_name = pycsw_config.get('repository', 'table')
    
    log1.info('Initialized module globals from Pylons config')
    
    return

def get_repo():
    '''Initialize (once) and return the pyCSW repository.
    '''
    
    global _repo

    if not _repo:
        _repo = pycsw.repository.Repository(
            pycsw_database, pycsw_context, table=pycsw_table_name)

    return _repo

def delete_record(session, pkg_dict):
    '''Delete the corresponding CSW record (if exists)
    '''
    
    repo = get_repo()
    
    existing_record = session.query(repo.dataset).get(pkg_dict['id'])
    if existing_record:
        session.delete(existing_record)
        session.commit()
    
    return existing_record

def create_or_update_record(session, pkg_dict):
    '''Create or update a CSW record to sync with a newly updated dataset
    '''
    
    repo = get_repo()
    
    existing_record = session.query(repo.dataset).get(pkg_dict['id'])
    
    record = make_record(pkg_dict, repo)
    if not record:
        return None
    
    # Now, a record object is computed from dataset's metadata

    if not existing_record:
        # Persist the newly created record
        session.add(record)
    else:
        # Copy new record to session-persistent object
        for key in map(lambda col: col.key, repo.dataset.__table__.columns):
            if key in ['identifier']:
                continue
            setattr(existing_record, key, getattr(record, key, None))
    
    session.commit()
    return record

def make_record(pkg_dict, repo=None):
    '''Build and return a metadata record from a dataset's XML dump.
    
    Returns None on failure, or a loaded metadata record on success.
    '''
    
    global pycsw_context

    if not repo:
        repo = get_repo()

    # Load pkg-dict into a metadata object

    pkg_id = pkg_dict['id']
    pkg_dtype = pkg_dict.get('dataset_type')
    obj = make_metadata_object(pkg_dtype, pkg_dict)
    
    # Generate an XML dump for current pkg-dict

    xser = xml_serializer_for(obj)
    xser.target_namespace = site_url 
    xmldata = xser.to_xml()
    
    # Parse XML dump into a pyCSW metadata record

    record = None
    try:
        record = pycsw.metadata.parse_record(pycsw_context, xmldata, repo)[0]
    except Exception as err:
        log1.error('Cannot extract metadata for %s: %s' % (pkg_id, err))
    else:
        log1.debug('Extracted metadata for dataset %s' % (pkg_id))

    # Note The following should always hold true when #13 is resolved, and
    # identifier is linked to package.id at validation phase.
    #assert record.identifier == pkg_id
    if record:
        record.identifier = pkg_id
    
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

