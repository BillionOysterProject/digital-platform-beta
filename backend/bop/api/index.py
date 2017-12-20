from __future__ import absolute_import
from __future__ import unicode_literals
from flask import jsonify
from .endpoints import Endpoint


class Index(Endpoint):
    route_prefix = '/'

    def index(self):
        return jsonify({
            'status': 'ok'
        })
