import re
#import tidylib
from lxml import etree


import ckan.plugins.toolkit as toolkit

def to_c14n_markup(markup, with_comments=True, pretty=False):
    if not isinstance(markup, basestring):
        markup = unicode(markup)
    el = etree.fromstring(markup)
    markup = etree.tostring(
        el, method='c14n', with_comments=with_comments, pretty_print=pretty)
    return toolkit.literal(markup.decode('utf-8'))

def to_tidy_markup(markup, extra_opts={}):
    tidy_opts = { 'hide-comments': False, 'show-body-only': True, }
    tidy_opts.update(extra_opts)
    markup, errors = tidylib.tidy_document(markup, options=tidy_opts)
    return markup

