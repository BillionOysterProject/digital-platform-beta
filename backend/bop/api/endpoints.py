from __future__ import absolute_import
from __future__ import unicode_literals
from flask import jsonify, request, g, Response
from flask_classy import FlaskView, route
from collections import OrderedDict
import pivot.exceptions
from ..utils import as_bool
from ..time import Time
import os
import dpath.util
import six
import unicodecsv
import io


class Endpoint(FlaskView):
    results_only = True
    strict_slashes = False
    route_prefix = '/api/'
    expand_fields = {}

    @classmethod
    def register(cls, app):
        cls._app = app
        cls.client = app.db
        super(Endpoint, cls).register(app)

    @property
    def app(self):
        return self._app

    @classmethod
    def collection_for(cls, name):
        return cls.client.collection(name)


class CollectionView(Endpoint):
    default_sort = None

    @classmethod
    def register(cls, app):
        super(CollectionView, cls).register(app)

    @property
    def collection(self):
        return self.client.collection(self.collection_name)

    @property
    def filter_params(self):
        params = {}

        if 'limit' in request.args:
            if request.args['limit'].lower() == 'false':
                params['limit'] = 2147483647
            else:
                params['limit'] = int(request.args['limit'])

        if 'offset' in request.args:
            params['offset'] = int(request.args['offset'])

        if 'fields' in request.args:
            params['fields'] = request.args['fields'].split(',')

        if 'sort' in request.args:
            params['sort'] = request.args['sort'].split(',')
        elif isinstance(self.default_sort, list):
            params['sort'] = self.default_sort

        return params

    @property
    def query_results_params(self):
        params = {}

        if 'expand' in request.args:
            params['expand'] = as_bool(request.args['expand'])

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

        # hang onto expanded results for the duration of this call so we don't needlessly
        # hammer the database with repeat calls during this process
        _result_cache = {}

        if len(self.expand_fields):
            # for each result...
            for i, result in enumerate(results):
                if isinstance(result, dict):
                    # deep get the value from the result
                    for field, related in self.expand_fields.items():
                        if isinstance(related, tuple):
                            try:
                                value = dpath.util.get(dict(result), field, separator='.')
                            except KeyError:
                                continue

                            related_collection = related[0]

                            try:
                                related_fields = list(related[1])
                            except IndexError:
                                related_fields = None

                            output = None

                            # retrieved value is a list, expand each item
                            if isinstance(value, list):
                                output = []

                                for expand_id in value:
                                    try:
                                        cache_key = '{}:{}'.format(related_collection, expand_id)

                                        if cache_key not in _result_cache:
                                            _result_cache[cache_key] = dict(
                                                self.collection_for(related_collection).get(
                                                    expand_id,
                                                    fields=related_fields
                                                )
                                            )

                                        output.append(self._prepare_single_result(
                                            _result_cache[cache_key]
                                        ))
                                    except:
                                        output.append({})

                            elif isinstance(value, six.string_types + (int,)):
                                # unpack IDs into expanded objects
                                try:
                                    cache_key = '{}:{}'.format(related_collection, value)

                                    if cache_key not in _result_cache:
                                        _result_cache[cache_key] = dict(
                                            self.collection_for(related_collection).get(
                                                value,
                                                fields=related_fields
                                            )
                                        )

                                    output = self._prepare_single_result(_result_cache[cache_key])
                                except pivot.exceptions.RecordNotFound:
                                    output = {}

                            if output:
                                dpath.util.set(result, field, output, separator='.')

                        else:
                            raise TypeError("Expansion rule must be tuple(collection, [fields ..])")

                results[i] = result

        return results

    @route('/export')
    def index_as_csv(self):
        query = g.get('query', request.args.get('q', 'all'))
        params = self.filter_params

        if 'limit' not in params:
            params['limit'] = False

        results = self.collection.query(query, **params)
        output = io.BytesIO()
        data = []

        fieldnames = ['id']

        for record in results:
            for k, v in record.items():
                if isinstance(v, (dict, list, tuple)) or k.startswith('__'):
                    continue

                if k not in fieldnames:
                    fieldnames.append(k)

            data.append(dict([
                (k, v) for k, v in record.items() if k in fieldnames
            ]))

        writer = unicodecsv.DictWriter(output, fieldnames=fieldnames, dialect='excel-tab')

        writer.writeheader()

        for record in data:
            writer.writerow(dict(record))

        output.seek(0)

        return Response(
            response=output,
            mimetype='text/tab-separated-values; charset=UTF-8',
            headers={
                'Content-Disposition': 'attachment; filename={}-{}.tsv'.format(
                    os.path.basename(
                        os.path.dirname(request.path)
                    ),
                    Time().isoformat()
                ),
            }
        )

    def index(self):
        query = g.get('query', request.args.get('q', 'all'))
        results = self.collection.query(query, **self.filter_params)
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
