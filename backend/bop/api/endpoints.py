from __future__ import absolute_import
from __future__ import unicode_literals
import os
import dpath.util
import six
import unicodecsv
import io
import logging
import pivot.exceptions
from flask import jsonify, request, g, Response
from flask_classy import FlaskView, route
from flask_login import current_user
from collections import OrderedDict
from ..accesscontrol import verify_path_is_authorized
from geojson import Feature, Point, FeatureCollection
from ..utils import as_bool
from ..time import Time
from ..user import User


class Endpoint(FlaskView):
    results_only = True
    strict_slashes = False
    route_prefix = '/api/'
    expand_fields = {}
    _app = None
    aggregateFns = (
        'sum',
        'average',
        'minimum',
        'maximum',
    )

    @classmethod
    def register(cls, app):
        cls._app = app
        cls.client = app.db
        super(Endpoint, cls).register(app)

    @property
    def app(self):
        return self.__class__._app

    @property
    def current_user(self):
        try:
            return User.get(current_user['id'])
        except:
            return None

    @classmethod
    def collection_for(cls, name):
        return cls.client.collection(name)

    # !! IMPORTANT !! FOOTGUN ALERT !! IMPORTANT !!
    # ----------------------------------------------------------------------------------------------
    # This is where ALL user authorization checks are performed.  Changing this
    # can accidentally expose all data to h@ckerz.
    def before_request(self, *args, **kwargs):
        verify_path_is_authorized(self, request)


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
                params['limit'] = False
            else:
                params['limit'] = int(request.args['limit'])

        if 'offset' in request.args:
            params['offset'] = int(request.args['offset'])
        else:
            params['offset'] = 0

        if 'fields' in request.args:
            params['fields'] = request.args['fields'].split(',')
        else:
            params['fields'] = []

        if 'sort' in request.args:
            params['sort'] = request.args['sort'].split(',')
        elif isinstance(self.default_sort, list):
            params['sort'] = self.default_sort
        else:
            params['sort'] = None

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
                    expand_keys = sorted(self.expand_fields.keys())

                    # deep get the value from the result
                    for field in expand_keys:
                        related = self.expand_fields[field]

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
                                        logging.warning('{}/{}: Field {} contains reference to missing record: {}/{}'.format(
                                            self.collection.name,
                                            result.id,
                                            field,
                                            related_collection,
                                            expand_id
                                        ))
                                        continue

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
                                    output = None

                            dpath.util.set(result, field, output, separator='.')

                        else:
                            raise TypeError(
                                "Expansion rule must be tuple(collection, [fields ..])"
                            )

                results[i] = result

        return results

    @route('/metrics')
    def metrics(self):
        query = g.get('query', request.args.get('q', 'all'))

        output = {
            'count': self.collection.count(query),
        }

        for pair in request.args.get('fn', '').split(','):
            parts = pair.split(':', 2)

            if len(parts) == 2:
                fn, field = parts

                if  fn in self.aggregateFns:
                    output[fn] = getattr(self.collection, fn)(field, query)

        return jsonify(output)

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
        if len(params['fields']):
            new_fields = []

            for p in params['fields']:
                if '.' in p:
                    has_nested_fields = True

                new_fields.append(p.split('.')[0])

            params['fields'] = list(set(new_fields))

        query_results_params = self.query_results_params
        query_results_params['raw'] = True
        query_results_params['expand'] = request.args.get('expand', has_nested_fields)

        if 'limit' not in params:
            params['limit'] = False

        results = self.collection.query(query, **params)
        results = self._prepare_query_results(results, **query_results_params)

        output = io.BytesIO()
        data = []

        fieldnames = []

        for record in results:
            record = dict(record)
            fields_to_retrieve = []
            output_record = OrderedDict()

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
            writer.writerow(record)

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
        return self._get_query_results(request.args.get('q', 'all'))

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

    def _get_query_results(self, query=None, params=None, raw=None, expand=None):
        query = g.get('query', (query or 'all'))
        qrp = self.query_results_params

        if isinstance(raw, bool):
            qrp['raw'] = raw

        if isinstance(expand, bool):
            qrp['expand'] = expand

        filters = self.filter_params

        if isinstance(params, dict):
            filters.update(params)

        results = self.collection.query(query, **filters)
        return self._prepare_query_results(results, **qrp)


class GeoCollectionView(CollectionView):
    latitude_field = 'latitude'
    longitude_field = 'longitude'
    results_only = True

    @property
    def geo_filter_params(self):
        params = super(GeoCollectionView, self).filter_params

        if len(params['fields']):
            if not self.latitude_field in params['fields']:
                params['fields'].append(self.latitude_field)

            if not self.longitude_field in params['fields']:
                params['fields'].append(self.longitude_field)

        if 'limit' not in params:
            params['limit'] = False

        return params

    @route('/export.geojson')
    def index_as_geojson(self):
        results = self._get_query_results(
            request.args.get('q'),
            params=self.geo_filter_params,
            raw=True
        )

        features = []

        for result in results:
            lng = result.get(self.longitude_field)
            lat = result.get(self.latitude_field)

            if lat is not None and lng is not None:
                point = Point((float(lng), float(lat)))
                result = dict(result)

                del result[self.latitude_field]
                del result[self.longitude_field]

                features.append(Feature(geometry=point, properties=result))

        return jsonify(FeatureCollection(features))
