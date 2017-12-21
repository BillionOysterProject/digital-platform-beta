from __future__ import absolute_import
from __future__ import unicode_literals
from flask import jsonify
from .endpoints import Endpoint


class Index(Endpoint):
    route_base = '/'

    def index(self):
        return jsonify({
            'status': 'ok',
        })

    def routes(self):
        return jsonify(self.app.list_routes())
