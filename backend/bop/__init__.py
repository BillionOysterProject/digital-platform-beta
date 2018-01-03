from __future__ import absolute_import
from __future__ import unicode_literals
import logging
import sys
import urllib
import inspect
import pivot
from flask import Flask, jsonify, url_for
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException
from .api.endpoints import Endpoint, CollectionView
from .api import *
from collections import OrderedDict


def handle_error(e):
    code = 500

    if isinstance(e, HTTPException):
        if e.code >= 300 and e.code < 400:
            return e

        code = e.code

    return jsonify(error=str(e)), code


class API(Flask):
    @property
    def db(self):
        if not hasattr(self, '_db'):
            self._db = pivot.Client()
        return self._db

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
                            names.add(name)
                            endpoints.add(obj)

        for obj in endpoints:
            obj.register(self)

    def list_routes(self):
        output = []

        for rule in self.url_map.iter_rules():
            options = OrderedDict({
                'arguments': [],
            })

            urlargs = {}

            for arg in rule.arguments:
                options['arguments'].append(arg)
                urlargs[arg] = ':{}'.format(arg)

            options['methods'] = sorted(
                [r for r in rule.methods if r not in ['HEAD', 'OPTIONS']]
            )

            options['url'] = url_for(rule.endpoint, **urlargs)

            output.append(options)

        return sorted(output, key=lambda v: v.get('url'))

    def run(self, *args, **kwargs):
        self.setup_error_intercept()
        self.autoregister_routes()

        super(API, self).run(*args, **kwargs)