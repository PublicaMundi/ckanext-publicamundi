import pylons.config as config
from pylons import request

from ckan.lib import helpers
from ckan.lib.base import (redirect, BaseController, render)
import ckan.plugins.toolkit as toolkit
import ckan.model as model

from ckanext.publicamundi.themes.geodata.plugin import get_contact_point

class Controller(BaseController):
    def send_email(self):
        sender_name = request.params.get("name")
        sender_email = request.params.get("email")
        pkg_name = request.params.get("pkg_name")
        text = request.params.get("message")
        antispam = request.params.get("antispam")

        assert not antispam

        # Find a better way to do this
        body = "Name: "
        body += sender_name
        body += "\nEmail: "
        body += sender_email
        body += "\nMessage: "
        body += text

        package = toolkit.get_action('package_show')({}, data_dict={'id':pkg_name})

        subject = 'Regarding: {0}'.format(package.get('title'))

        contact_point = get_contact_point(package)

        contact_point_name = contact_point.get('name')
        contact_point_email = contact_point.get('email')

        cc_email = config.get("email_to")
        cc_name = config.get("ckan.site_title").decode('utf-8')

        import ckan.lib.mailer

        try:
           ckan.lib.mailer.mail_recipient(contact_point_name, cc_email,subject, body)
        except ckan.lib.mailer.MailerException:
            raise

