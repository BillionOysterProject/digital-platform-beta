from __future__ import absolute_import
from __future__ import unicode_literals
from flask import jsonify, request
from flask_classy import FlaskView
from collections import OrderedDict


class Endpoint(FlaskView):
    route_prefix = '/api/'


class CollectionView(Endpoint):
    @classmethod
    def register(cls, app):
        # TODO: make sure cls.collection_name is a string
        cls.client = app.db
        super(CollectionView, cls).register(app)

    @property
    def collection(self):
        return self.client.collection(self.collection_name)

    @property
    def filter_params(self):
        params = {}

        if 'limit' in request.args:
            params['limit'] = int(request.args['limit'])

        if 'offset' in request.args:
            params['offset'] = int(request.args['offset'])

        if 'sort' in request.args:
            params['sort'] = request.args['sort'].split(',')

        return params

    def prepare_results(self, results):
        return jsonify(OrderedDict({
            'totalCount':         results.result_count,
            self.collection_name: list(results)
        }))

    def index(self):
        results = self.collection.query(request.args.get('q', 'all'), **self.filter_params)
        return self.prepare_results(results)


    def get(self, record_id):
        return jsonify(self.collection.get(record_id))
