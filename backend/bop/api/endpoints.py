from __future__ import absolute_import
from __future__ import unicode_literals
from flask import jsonify, request
from flask_classy import FlaskView
from collections import OrderedDict
import pivot.exceptions


class Endpoint(FlaskView):
    results_only = False
    strict_slashes = False
    route_prefix = '/api/'
    expand_fields = {}

    @classmethod
    def register(cls, app):
        cls._app = app
        super(Endpoint, cls).register(app)

    @property
    def app(self):
        return self._app


class CollectionView(Endpoint):
    default_sort = None

    @classmethod
    def register(cls, app):
        # TODO: make sure cls.collection_name is a string

        cls._app = app
        cls.client = app.db
        super(CollectionView, cls).register(app)

    @classmethod
    def collection_for(cls, name):
        return cls.client.collection(name)

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
        elif isinstance(self.default_sort, list):
            params['sort'] = self.default_sort

        return params

    @property
    def query_results_params(self):
        params = {}

        if 'expand' in request.args:
            params['expand'] = (request.args['expand'].lower() in ['true', '1', 'yes'])

        return params

    @property
    def single_result_params(self):
        return {}

    def _prepare_query_results(self, results, expand=True):
        if expand:
            data = [
                self._prepare_single_result(r) for r in self._expand_results(
                    list(results)
                )
            ]
        else:
            data = [
                self._prepare_single_result(r) for r in results
            ]

        if self.results_only:
            return jsonify(data)
        else:
            return jsonify(OrderedDict({
                'totalCount':         results.result_count,
                self.collection_name: data,
            }))

    def _prepare_single_result(self, result):
        try:
            result['_id'] = result.pop('id')
        except KeyError:
            pass

        return result

    def _expand_results(self, results):
        """
        Performs object reference expansion, configurable on a per-collection basis.
        """
        if len(self.expand_fields):
            # for each result...
            for i, result in enumerate(results):
                if isinstance(result, dict):
                    # for each k-v pair
                    for k, v in result.items():
                        if k in self.expand_fields:
                            related = self.expand_fields[k]
                            related_collection = k
                            fields = []

                            if isinstance(related, list):
                                # list means just use the field name as the collection and only
                                # retrieve the given fields
                                fields = related

                            elif isinstance(related, tuple):
                                # tuple means that the first arg is the collection, the second is
                                # the field list
                                related_collection = related[0]

                                try:
                                    fields = list(related[1])
                                except IndexError:
                                    pass

                            if isinstance(v, list):
                                # unpack lists of IDs into lists of expanded objects
                                result[k] = []

                                for vv in v:
                                    try:
                                        result[k].append(
                                            self._prepare_single_result(
                                                dict(self.collection_for(related_collection).get(
                                                    vv,
                                                    fields=fields
                                                ))
                                            )
                                        )
                                    except:
                                        result[k].append({})

                            elif isinstance(v, (basestring, int)):
                                # unpack IDs into expanded objects
                                try:
                                    result[k] = self._prepare_single_result(
                                        dict(self.collection_for(related_collection).get(
                                            v,
                                            fields=fields
                                        ))
                                    )
                                except pivot.exceptions.RecordNotFound:
                                    result[k] = {}
                results[i] = result

        return results

    def index(self):
        results = self.collection.query(request.args.get('q', 'all'), **self.filter_params)
        return self._prepare_query_results(results, **self.query_results_params)

    def get(self, record_id):
        result = self.collection.get(record_id)
        result = self._expand_results([result])[0]
        result = self._prepare_single_result(result, **self.single_result_params)

        return jsonify(result)

    def post(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass
