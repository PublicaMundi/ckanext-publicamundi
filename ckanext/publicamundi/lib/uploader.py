import os
import cgi
import datetime
import logging

from pylons import config

import ckan.lib.munge as munge

# Note
# We are going to reuse the file storage utility used by CKAN itself
# to store uploaded resources. However, this utility is not included
# in plugins toolkit (therefore, it could break anytime in the future).
from ckan.lib.uploader import get_storage_path, Upload, ResourceUpload

class MetadataUpload(Upload):
    '''Represents an uploaded file containing XML metadata.
    '''

    def __init__(self, old_filename=None):
        super(MetadataUpload, self).__init__('source-metadata', old_filename)

    def update_data_dict(self, data_dict, file_field):
        super(MetadataUpload, self).update_data_dict(data_dict, '', file_field, '')

    def get_path(self, name):
        return os.path.join(self.storage_path, name)
