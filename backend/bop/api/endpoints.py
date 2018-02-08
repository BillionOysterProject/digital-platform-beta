from __future__ import absolute_import
from __future__ import unicode_literals
from flask import jsonify, request, g, Response
from flask_classy import FlaskView, route
from flask_login import current_user
from collections import OrderedDict
import pivot.exceptions
from ..utils import as_bool
from ..time import Time
from ..user import User
import os
import dpath.util
import six
import unicodecsv
import io
import logging


class Endpoint(FlaskView):
    results_only = True
    strict_slashes = False
    route_prefix = '/api/'
    expand_fields = {}
    app = None

    @classmethod
    def register(cls, app):
        cls.app = app
        cls.client = app.db
        super(Endpoint, cls).register(app)

    @property
    def app(self):
        return self.__class__.app

    @property
    def current_user(self):
        try:
            return User.get(current_user['id'])
        except:
            return None

    @classmethod
    def collection_for(cls, name):
        return cls.client.collection(name)


class CollectionView(Endpoint):
    default_sort = None

    @classmethod
    def register(cls, app):
        super(CollectionView, cls).register(app)

    @classmethod
    def get_collection(cls):
        return cls.client.collection(cls.collection_name)

    @property
    def collection(self):
        return self.get_collection()

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

    def _prepare_query_results(self, results, expand=True, raw=False):
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

        if raw is True:
            return data
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

    @route('/export.tsv')
    def index_as_csv(self):
        query = g.get('query', request.args.get('q', 'all'))

        # get filter params from querystring
        params = self.filter_params

        # extract the untouched fields list
        fields = params.get('fields', [])
        has_nested_fields = False

        # if fields was specified, pass only the first dot-separated parts
        # this ensures the the database properly retrieves the FIELDS before
        # expansion occurs.
        if 'fields' in params and len(params['fields']):
            new_fields = []

            for p in params['fields']:
                if '.' in p:
                    has_nested_fields = True

                new_fields.append(p.split('.')[0])

            params['fields'] = list(set(new_fields))

        query_results_params = self.query_results_params
        query_results_params['raw'] = True
        query_results_params['expand'] = has_nested_fields

        if 'limit' not in params:
            params['limit'] = 2147483647

        results = self.collection.query(query, **params)
        results = self._prepare_query_results(results, **query_results_params)

        output = io.BytesIO()
        data = []

        fieldnames = []

        for record in results:
            record = dict(record)
            fields_to_retrieve = []
            output_record = {}

            if not len(fields):
                fields_to_retrieve = record.keys()
            else:
                fields_to_retrieve = fields

            if '_id' not in fields_to_retrieve:
                fields_to_retrieve = ['_id'] + fields_to_retrieve

            # actually pluck the values out of the response, doing a deep-get into
            # nested result dicts as necessary
            for field in fields_to_retrieve:
                if field.startswith('__'):
                    continue

                try:
                    value = dpath.util.get(record, field, separator='.')
                except KeyError:
                    value = None

                if value in [None, '']:
                    output_record[field] = None

                elif isinstance(value, dict):
                    continue

                elif isinstance(value, (list, tuple)):
                    output_record[field] = ','.join(['{}'.format(vv) for vv in value])

                elif isinstance(value, six.string_types):
                    output_record[field] = value.replace("\n", " ")

                else:
                    output_record[field] = value

                if field not in fieldnames:
                    fieldnames.append(field)

            data.append(output_record)

        logging.info(data)

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
