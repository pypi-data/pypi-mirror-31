import base64
import pickle
from datetime import timedelta
import datetime
import hmac
from hashlib import sha1
import os

from wtforms import Form
from wtforms.widgets import HiddenInput
from wtforms.csrf.session import SessionCSRF
from wtforms.csrf.core import CSRF
from wtforms import ValidationError

from multidict import CIMultiDict

from kaira.cookie import CookieManager


SUBMIT_METHODS = ('POST', 'PUT', 'PATCH', 'DELETE')


class KairaForm(Form):

    def __init__(self, request, **kwargs):

        self.request = request

        input_vars = dict()
        if request.method == 'GET':
            input_method = request.query
        elif request.method == 'POST':
            input_method = request.form

        for key, value in input_method.items():
            if isinstance(value, list) and len(value) == 1:
                value = value[0]
            input_vars[key] = value

        input_vars = CIMultiDict(**input_vars)

        super().__init__(formdata=input_vars, **kwargs)

    def is_submitted(self):
        """Consider the form submitted if there is an active request and
        the method is ``POST``, ``PUT``, ``PATCH``, or ``DELETE``.
        """

        return bool(self.request) and self.request.method in SUBMIT_METHODS

    def validate_on_submit(self):
        """Call :meth:`validate` only if the form is submitted.
        This is a shortcut for ``form.is_submitted() and form.validate()``.
        """
        return self.is_submitted() and self.validate()

    def hidden_tag(self, *fields):
        """Render the form's hidden fields in one call.
        A field is considered hidden if it uses the
        :class:`~wtforms.widgets.HiddenInput` widget.
        If ``fields`` are given, only render the given fields that
        are hidden.  If a string is passed, render the field with that
        name if it exists.
        .. versionchanged:: 0.13
           No longer wraps inputs in hidden div.
           This is valid HTML 5.
        .. versionchanged:: 0.13
           Skip passed fields that aren't hidden.
           Skip passed names that don't exist.
        """

        def hidden_fields(fields):
            for f in fields:
                if isinstance(f, str):
                    f = getattr(self, f, None)

                if f is None or not isinstance(f.widget, HiddenInput):
                    continue

                yield f

        return u'\n'.join(str(f) for f in hidden_fields(fields or self))

    def render_boostrap_fields(self):
        """ Render fields"""

        xml_form = list()
        for field in self:
            if field.id == 'csrf_token':  # salteamos el csrf token
                continue
            xml_field = list()
            xml_field.append('%s' % field.label)
            xml_field.append('%s' % field(class_='form-control'))
            if field.errors:
                xml_error = list()
                for error in field.errors:
                    xml_error.append('<li>%s</li>' % error)
                xml_field.append('<small class="form-text text-muted">%s</small>' % '\n'.join(xml_error))
            xml_form.append('<div class="form-group">%s</div>' % '\n'.join(xml_field))
        return '\n'.join(xml_form)

    def render_boostrap_form(self, path='/'):
        """ Render form"""

        r_fields = self.render_boostrap_fields()
        submit = '<button type="submit"> Send </button>'
        xml = '<form method="POST" enctype="multipart/form-data" action="{path}">{fields} {submit}</form>'\
            .format(path=path, fields=r_fields, submit=submit)
        return xml


# class KairaSessionCSRF(dict):
#
#     def __init__(self, request):
#         super().__init__()
#         self.request = request
#
#     def __setitem__(self, key, value):
#         self.set_token_cookie()
#         if value is not False:
#             return super().__setitem__(key, value)
#
#     def get_token_cookie(self, request):
#
#         cookie_name = 'csrf'
#         cookie = request.cookies.get(cookie_name, None)
#         return cookie
#
#     def set_token_cookie(self, ticket, request):
#
#         expire_seconds = int(config['OAUTH2_COOKIE_EXPIRE'])
#
#         if expire_seconds > 0:
#             now = datetime.datetime.utcnow()
#             expires = now + datetime.timedelta(seconds=expire_seconds)
#         else:
#             expires = None
#
#         if config['OAUTH2_SECURE_COOKIE'] == 'True':
#             secure_cookie = True
#         else:
#             secure_cookie = False
#
#         cookie_name = config['OAUTH2_COOKIE_NAME']
#         cookie_domain = config['OAUTH2_COOKIE_DOMAIN']
#
#         if not cookie_domain or cookie_domain == "":
#             domain = request.host.split(':')[0]
#         else:
#             domain = cookie_domain
#
#         cookie_options = {
#             'HTTP_COOKIE_DOMAIN': domain,
#             'HTTP_COOKIE_SECURE': secure_cookie,
#             'HTTP_COOKIE_HTTPONLY': True
#         }
#
#         cookies = CookieManager(options=cookie_options)
#         cookies[cookie_name] = str(ticket)
#         cookies[cookie_name].path = '/'
#         cookies[cookie_name].expires = expires
#
#         return cookies


# class KairaFormCSRF(KairaForm):
#
#     def __init__(self, request, **kwargs):
#         self.request = request
#         self.csrf = True
#         self.csrf_class = SessionCSRF
#         self.csrf_secret = b'EPj00jpfj8Gx1SjnyLxwBBSQfnQ9DJYe0Ym'
#         self.csrf_time_limit = timedelta(minutes=60)
#         self.csrf_context = '123456789abcdefghijklmn'
#         super().__init__(request=request, **kwargs)


# class KairaFormCSRF(KairaForm):
#
#     class Meta:
#         csrf = True
#         csrf_class = SessionCSRF
#         csrf_secret = b'EPj00jpfj8Gx1SjnyLxwBBSQfnQ9DJYe0Ym'
#         csrf_time_limit = timedelta(minutes=20)
#
#         @property
#         def csrf_context(self):
#             session = dict()
#             session['csrf'] = '123456789abcdefghijklmn'
#             return session


class KSessionCSRF(CSRF):
    TIME_FORMAT = '%Y%m%d%H%M%S'

    def setup_form(self, form):

        self.form_meta = form.meta
        return super(KSessionCSRF, self).setup_form(form)

    def create_session(self):

        meta = self.form_meta
        expire_seconds = int(meta.csrf_options['CSRF_COOKIE_EXPIRE'])
        if expire_seconds > 0:
            now = datetime.datetime.utcnow()
            expires = now + datetime.timedelta(seconds=expire_seconds)
        else:
            expires = None

        if not meta.csrf_options['CSRF_COOKIE_DOMAIN'] or meta.csrf_options['CSRF_COOKIE_DOMAIN'] == "":
            domain = meta.request.host.split(':')[0]
        else:
            domain = meta.csrf_options['CSRF_COOKIE_DOMAIN']

        cookies_options = {
            'HTTP_COOKIE_DOMAIN': domain,
            'HTTP_COOKIE_SECURE': meta.csrf_options['CSRF_COOKIE_SECURE'],
            'HTTP_COOKIE_HTTPONLY': meta.csrf_options['CSRF_COOKIE_HTTPONLY']
        }

        cookie_name = meta.csrf_options['CSRF_COOKIE_NAME']

        session = meta.session
        if not session:
            session = CookieManager(options=cookies_options)
        session[cookie_name] = sha1(os.urandom(64)).hexdigest()  # request.cookies.get(cookie_name, None)
        session[cookie_name].path = meta.csrf_options['CSRF_COOKIE_PATH']
        session[cookie_name].expires = expires

        return session

    def generate_csrf_token(self, csrf_token_field):

        meta = self.form_meta

        """
        csrf_options = {
            'CSRF_COOKIE_DOMAIN': '',
            'CSRF_COOKIE_SECURE': False,
            'CSRF_COOKIE_HTTPONLY': True,
            'CSRF_COOKIE_EXPIRE': 0,
            'CSRF_COOKIE_PATH': '/',
            'CSRF_COOKIE_NAME': 'csrf',
            'CSRF_SECRET': b'APj00jpfj8Gx1SjnyLxwBBSQfnQ9DJYe0Cm',
            'CSRF_TIME_LIMIT': timedelta(minutes=60)            
            }
        """

        time_limit = meta.csrf_options['CSRF_TIME_LIMIT']
        csrf_secret = meta.csrf_options['CSRF_SECRET']

        if csrf_secret is None:
            raise Exception('must set `csrf_secret` on class Meta for SessionCSRF to work')
        #if meta.csrf_context is None:
        #    raise TypeError('Must provide a session-like object as csrf context')

        session = meta.session

        if not session or 'csrf' not in session:
            print("ENTRA")
            meta.session = self.create_session()
            #session['csrf'] = sha1(os.urandom(64)).hexdigest()

        print(meta.session)

        if time_limit:
            expires = (self.now() + time_limit).strftime(self.TIME_FORMAT)
            csrf_build = '%s%s' % (meta.session['csrf'], expires)
        else:
            expires = ''
            csrf_build = meta.session['csrf']

        hmac_csrf = hmac.new(csrf_secret, csrf_build.encode('utf8'), digestmod=sha1)
        return '%s##%s' % (expires, hmac_csrf.hexdigest())

    def validate_csrf_token(self, form, field):

        meta = self.form_meta

        time_limit = meta.csrf_options['CSRF_TIME_LIMIT']
        csrf_secret = meta.csrf_options['CSRF_SECRET']

        if not field.data or '##' not in field.data:
            raise ValidationError(field.gettext('CSRF token missing'))

        expires, hmac_csrf = field.data.split('##', 1)

        check_val = (str(meta.session['csrf']) + expires).encode('utf8')

        hmac_compare = hmac.new(csrf_secret, check_val, digestmod=sha1)
        if hmac_compare.hexdigest() != hmac_csrf:
            raise ValidationError(field.gettext('CSRF failed'))

        if time_limit:
            now_formatted = self.now().strftime(self.TIME_FORMAT)
            if now_formatted > expires:
                raise ValidationError(field.gettext('CSRF token expired'))

    def now(self):
        """
        Get the current time. Used for test mocking/overriding mainly.
        """
        return datetime.datetime.now()

    @property
    def time_limit(self):
        return getattr(self.form_meta, 'csrf_time_limit', timedelta(minutes=30))

    @property
    def session(self):
        return getattr(self.form_meta.csrf_context, 'session', self.form_meta.csrf_context)


class KairaFormCSRF(KairaForm):

    class Meta:
        csrf = True
        csrf_class = KSessionCSRF
        csrf_options = {
            'CSRF_COOKIE_DOMAIN': '',
            'CSRF_COOKIE_SECURE': False,
            'CSRF_COOKIE_HTTPONLY': True,
            'CSRF_COOKIE_EXPIRE': 0,
            'CSRF_COOKIE_PATH': '/',
            'CSRF_COOKIE_NAME': 'csrf',
            'CSRF_SECRET': b'APj00jpfj8Gx1SjnyLxwBBSQfnQ9DJYe0Cm',
            'CSRF_TIME_LIMIT': timedelta(minutes=60)
            }
        #request = None
        #session = None
        #csrf_secret = b'EPj00jpfj8Gx1SjnyLxwBBSQfnQ9DJYe0Ym'
        #cookies = dict(csrf='')

        # @property
        # def csrf_context(self):
        #     return self.session

    def __init__(self, request, cookies=None, csrf_options=None, **kwargs):

        self.request = request
        self.csrf_options = csrf_options
        self.cookies = cookies
        if not csrf_options:
            csrf_options = {
                'CSRF_COOKIE_DOMAIN': '',
                'CSRF_COOKIE_SECURE': False,
                'CSRF_COOKIE_HTTPONLY': True,
                'CSRF_COOKIE_EXPIRE': 0,
                'CSRF_COOKIE_PATH': '/',
                'CSRF_COOKIE_NAME': 'csrf',
                'CSRF_SECRET': b'APj00jpfj8Gx1SjnyLxwBBSQfnQ9DJYe0Cm',
                'CSRF_TIME_LIMIT': timedelta(minutes=60)
            }

        super().__init__(request=request, meta=dict(session=cookies, request=request, csrf_options=csrf_options, csrf_context=cookies), **kwargs)

        #self.meta.csrf = True
        #self.meta.csrf_class = SessionCSRF
        #self.meta.csrf_secret = csrf_options['CSRF_SECRET']
        #self.meta.csrf_time_limit = csrf_options['CSRF_TIME_LIMIT']
        #self.meta.cookies = cookies
        #self.meta.csrf_context = cookies


def read_in_chunks(file_object, chunk_size=1024):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


def upload_store(file_dest, upload_file):
    """Store the file"""

    upload_file.file.seek(0)
    for piece in read_in_chunks(upload_file.file):
        file_dest.write(piece)

    return file_dest


def serialize(obj):
    return base64.b64encode(pickle.dumps(obj))


def deserialize(s):
    return pickle.loads(base64.b64decode(s))

