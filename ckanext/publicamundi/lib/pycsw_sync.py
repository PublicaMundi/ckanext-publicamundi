import sys
import logging
import datetime
import io

import requests
from lxml import etree

from pylons import config as pylons_config

from pycsw import metadata, repository, util
import pycsw.config
import pycsw.admin

log1 = logging.getLogger(__name__)

pycsw_config_path = pylons_config.get('ckanext.publicamundi.pycsw.config')
pycsw_config = _load_config(pycsw_config_path)
pycsw_context = pycsw.config.StaticContext()
pycsw_database = pycsw_config.get('repository', 'database')
pycsw_table_name = pycsw_config.get('repository', 'table')
pycsw_repo = repository.Repository(pycsw_database, pycsw_context, table=pycsw_table_name)

def create(ckan_id,context=pycsw_context,repo=pycsw_repo):
	ckan_url = pylons_config.get('ckan.site_url')
	record = get_record(context, repo, ckan_url, ckan_id)
    if not record:
        log1.error('Skipped record %s' % ckan_id)
        continue
    try:
        repo.insert(record, 'local', util.get_today_and_now())
        log1.info('Inserted %s' % ckan_id)
    except Exception, err:
        log1.error('ERROR: not inserted %s Error:%s' % (ckan_id, err))

def update(ckan_id,context=pycsw_context,repo=pycsw_repo):
	ckan_url = pylons_config.get('ckan.site_url')
    record = get_record(context, repo, ckan_url, ckan_id)
    if not record:
    	log1.error('Skipped record %s' % ckan_id)
        continue
    update_dict = dict([(getattr(repo.dataset, key),
    getattr(record, key)) \
    for key in record.__dict__.keys() if key != '_sa_instance_state'])
    try:
        repo.session.begin()
        repo.session.query(repo.dataset).filter_by(
        ckan_id=ckan_id).update(update_dict)
        repo.session.commit()
        log1.info('Changed %s' % ckan_id)
    except Exception, err:
        repo.session.rollback()
        raise RuntimeError, 'ERROR: %s' % str(err)

def get_record(context, repo, ckan_url, ckan_id):
    api_url = 'api/publicamundi/dataset/export/%s' % ckan_id
    query = ckan_url + api_url
    response = requests.get(url)

    try:
        xml = etree.parse(io.BytesIO(response.content))
    except Exception, err:
        log1.error('Could not pass xml doc from %s, Error: %s' % (ckan_id, err))
        return

    try:
        record = metadata.parse_record(context, xml, repo)[0]
    except Exception, err:
        log1.error('Could not extract metadata from %s, Error: %s' % (ckan_id, err))
        return

    if not record.identifier:
        record.identifier = ckan_id

    return record

def _load_config(file_path):
    abs_path = os.path.abspath(file_path)
    if not os.path.exists(abs_path):
        raise AssertionError('pycsw config file {0} does not exist.'.format(abs_path))

    config = SafeConfigParser()
    config.read(abs_path)
    return config