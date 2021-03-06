from __future__ import absolute_import
from __future__ import unicode_literals
import sys
import logging
import os
import inspect
import pivot
from traceback import format_exc
from .utils import parse_docstring, as_bool
from .api import *
from flask import Flask, jsonify, url_for
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException
from .api.endpoints import Endpoint, CollectionView
from collections import OrderedDict
from flask_login import LoginManager
from flask_session import Session
import sentry_sdk
from raven.contrib.flask import Sentry
from raven.conf import setup_logging
import redis


def handle_error(e):
    code = 500

    if isinstance(e, HTTPException):
        if e.code >= 300 and e.code < 400:
            return e

        code = e.code

    if code not in [401, 403, 404]:
        logging.warning(e)

    response = {
        'error': '{}'.format(e),
    }

    return jsonify(**response), code


class API(Flask):
    @property
    def db(self):
        if not hasattr(self, '_db'):
            self._db = pivot.Client()
        return self._db

    def setup_sentry_reporting(self):
        # setup Sentry error reporting (only works if SENTRY_DSN envvar is set)
        # self.sentry = Sentry(self, logging=True, level=logging.INFO)
        # sentry_sdk.init(os.getenv('SENTRY_DSN'))
        pass

    def setup_persistent_sessions(self):
        self.session_manager = Session()

        self.secret_key = os.urandom(32)

        try:
            self.config['SESSION_TYPE'] = 'redis'
            conn = redis.Redis(
                host=os.getenv('SESSION_REDIS_HOST', 'localhost'),
                port=int(os.getenv('SESSION_REDIS_PORT', 6379))
            )

            conn.ping()
            self.config['SESSION_REDIS'] = conn
        except redis.exceptions.ConnectionError as e:
            logging.warning('Failed to connect to Redis: {}'.format(e))
            logging.warning('Falling back to local-only session store.')
            logging.warning('Session data will not be shared between multiple servers.')
            logging.warning('This will make staying logged-in to the site annoying in multi-server deployments.')
            self.config['SESSION_TYPE'] = 'filesystem'

        self.session_manager.init_app(self)

    def setup_login_manager(self):
        self.login_manager = LoginManager()
        self.login_manager.init_app(self)

    def setup_error_intercept(self):
        self.handle_http_exception = handle_error

        for ex in default_exceptions:
            self.register_error_handler(ex, handle_error)

    def autoregister_routes(self):
        names = set()
        endpoints = set()

        for key, module in sys.modules.items():
            if key.startswith('bop.api.'):
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, Endpoint) and obj not in [
                        Endpoint,
                        CollectionView,
                    ]:
                        if name not in names:
                            logging.info('Register endpoint: {} -> /api/{}'.format(name, obj.route_base))
                            names.add(name)
                            endpoints.add(obj)

        for obj in endpoints:
            obj.register(self)

    def list_routes(self):
        output = []

        for rule in self.url_map.iter_rules():
            methods = sorted(
                [r for r in rule.methods if r not in ['HEAD', 'OPTIONS']]
            )

            for method in methods:
                options = OrderedDict({
                    'arguments': [],
                })

                urlargs = {}

                for arg in rule.arguments:
                    options['arguments'].append(arg)
                    urlargs[arg] = ':{}'.format(arg)

                options['method'] = method
                options['url'] = url_for(rule.endpoint, **urlargs)

                obj = self.view_functions[rule.endpoint]
                doc = obj.__doc__

                if doc:
                    parsed = parse_docstring(doc)
                    options['description'] = parsed['short_description']

                    for i, opt in enumerate(options['arguments']):
                        options['arguments'][i] = {
                            'name': opt,
                        }

                    options['querystrings'] = []

                    try:
                        for param in parsed['params']:
                            for i, opt in enumerate(options['arguments']):
                                if opt['name'] == param['name']:
                                    options['arguments'][i]['description'] = param['doc']
                                    raise StopIteration

                            # if we got here, we're not describing a URL param, but a querystring
                            options['querystrings'].append({
                                'name':        param['name'],
                                'description': param['doc'].strip(),
                            })

                    except StopIteration:
                        pass

                output.append(options)

        return sorted(output, key=lambda v: v.get('url'))

    def setup(self):
        self.setup_sentry_reporting()
        self.setup_persistent_sessions()
        self.setup_login_manager()
        self.setup_error_intercept()
        self.autoregister_routes()

    def run(self, *args, **kwargs):
        super(API, self).run(*args, **kwargs)
