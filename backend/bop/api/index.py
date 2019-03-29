from __future__ import absolute_import
from __future__ import unicode_literals
from flask import jsonify
from .endpoints import Endpoint


class Index(Endpoint):
    route_base = '/'

    def index(self):
        self.client.collection('expeditions').count()

        return jsonify({
            'status':   'ok',
            'database': 'ok',
        })

    def routes(self):
        """
        A list of all supported API endpoints.
        """
        return jsonify(self.app.list_routes())
