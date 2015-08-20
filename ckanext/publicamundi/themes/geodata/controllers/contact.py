import base64
import StringIO
import json
from urlparse import urlparse

import pylons.config as config
from pylons import request, session

from ckan.lib import helpers
from ckan.lib.base import (redirect, BaseController, render, c)
import ckan.lib.mailer as mailer
import ckan.model as model
import ckan.plugins.toolkit as toolkit

from ckanext.publicamundi.themes.geodata.plugin import get_contact_point

_ = toolkit._

class Controller(BaseController):

    def send_email(self):
        sender_name = request.params.get("name")
        sender_email = request.params.get("email")
        pkg_name = request.params.get("pkg_name")
        message = request.params.get("message")
        antispam = request.params.get("antispam")
        captcha = request.params.get("captcha")

        # Assert request has been made with necessary post data
        
        assert captcha
        assert not antispam
        assert sender_name
        assert sender_email
        assert pkg_name
        assert message

        captcha_key = session.get('contact_form_captcha_key', None)
        if not captcha == captcha_key:
            return json.dumps({'success': False, 'error': 'wrong-captcha'})
        
        context = {
            'for_view': True,
            'user': c.user or c.author,
            'model': model,
            'session': model.Session,
            'api_version': 3
        }
        host = urlparse(config.get('ckan.site_url')).netloc
        package = toolkit.get_action('package_show')(context, data_dict={'id': pkg_name})
        subject = _('Contact: {0}').format(package.get('title'))
        contact_point = get_contact_point(package)
        
        body = toolkit.render_text('snippets/contact_message.txt', extra_vars={
            'subject': subject,
            'sender_name': sender_name,
            'sender_email': sender_email,
            'message': message,
            'pkg': package,
            'host': str(host),
        })
        cc_email = config.get("email_to")
        headers = {}
        if cc_email and (not cc_email == contact_point.get('email')):
            headers.update({
            'Cc': cc_email,
            })
        try:
            mailer.mail_recipient(
                #_('sir/madam'), 
                contact_point.get('name'), 
                contact_point.get('email'), 
                subject, 
                body, 
                headers=headers)
            return json.dumps({'success': True})
        except mailer.MailerException:
            #return json.dumps({'success': False, 'error': 'mail-not-sent'})
            raise

    def generate_captcha(self):
        from wheezy.captcha.image import captcha
        from wheezy.captcha.image import background
        from wheezy.captcha.image import curve
        from wheezy.captcha.image import noise
        from wheezy.captcha.image import smooth
        from wheezy.captcha.image import text

        from wheezy.captcha.image import offset
        from wheezy.captcha.image import rotate
        from wheezy.captcha.image import warp

        import random
        import string

        def _file_to_base64(stream):

            image_data = base64.b64encode(stream)
            return 'data:image/{0};base64,{1}'.format('captcha_image', image_data)

        captcha_image = captcha(drawings=[
            text(
                fonts = [
                    '/usr/share/fonts/truetype/ttf-dejavu/DejaVuSerif.ttf',
                    ],
                drawings=[
                    warp(0.5),
                    rotate(),
                    offset()
                ]),
            curve(),
            noise(),
            smooth()
        ], width=300)
        allowed_chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
        captcha_string = ''
        for i in range(0, 5):
            captcha_string += random.choice(allowed_chars)
        #captcha_string = list(random.sample(string.uppercase + string.digits, 4))
        session['contact_form_captcha_key'] = ''.join(captcha_string)
        session.save()

        image = captcha_image(captcha_string)

        output = StringIO.StringIO()
        image.save(output, 'JPEG', quality=75)
        contents = output.getvalue()

        return _file_to_base64(contents)
