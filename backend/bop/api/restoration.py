from __future__ import absolute_import
from __future__ import unicode_literals
from .endpoints import CollectionView, GeoCollectionView
from flask import Response, jsonify, request
from flask_classy import route
import requests
import dpath.util
import io
import logging
from .. import env
from ..time import Time
import unicodecsv
from sortedcontainers import SortedList


class ExpeditionActivities(CollectionView):
    route_base      = 'expedition-activities'
    collection_name = 'expeditionactivities'
    results_only    = True


class Expeditions(CollectionView):
    route_base      = 'expeditions'
    collection_name = 'expeditions'

    @route('/report')
    def report(self):
        from ..tasks.data import EXPEDITION_EXPORT_KEY

        bucket = env.get_reports_bucket()
        params = self.filter_params
        report = requests.get('https://{}.s3.amazonaws.com/{}'.format(
            bucket,
            EXPEDITION_EXPORT_KEY
        ))

        if report.status_code == 200:
            data = io.StringIO(report.text)
            outfields = set()
            reader = unicodecsv.DictReader(data, dialect='excel-tab')
            data = SortedList()

            for row in reader:
                if len(params['fields']):
                    for k, _ in row.items():
                        if k not in params['fields']:
                            del row[k]

                    outfields = params['fields']
                else:
                    outfields.update(row.keys())

                data.add(row)

            output = io.BytesIO()
            writer = unicodecsv.DictWriter(
                output,
                fieldnames=list(outfields),
                dialect='excel-tab'
            )
            writer.writeheader()

            for row in data:
                writer.writerow(row)

            output.seek(0)

            return Response(
                response=output,
                mimetype='text/tab-separated-values; charset=UTF-8',
                headers={
                    'Content-Disposition': 'attachment; filename=expeditions-{}.tsv'.format(
                        Time()
                    ),
                }
            )

        else:
            return None, report.status_code

    def photos(self):
        expeditions = self._get_query_results(
            request.args.get('q'),
            params={
                'fields': 'protocols',
            },
            raw=True,
            expand=False
        )

        images = []
        protoTables = {
            'protocolsiteconditions':     set(),
            'protocoloystermeasurements': set(),
            'protocolmobiletraps':        set(),
            'protocolsettlementtiles':    set(),
            'protocolwaterqualities':     set(),
        }

        protoImageFields = {
            'protocolsiteconditions':     (
                'landConditions.landConditionPhoto.path',
                'protocolsiteconditions.waterConditions.waterConditionPhoto.path',
            ),
            'protocoloystermeasurements': (
                'measuringOysterGrowth.substrateShells.*.innerSidePhoto.path',
                'measuringOysterGrowth.substrateShells.*.outerSidePhoto.path',
                'conditionOfOysterCage.oysterCagePhoto.path',
            ),
            'protocolmobiletraps':        (
                'mobileOrganisms.*.sketchphoto.path',
            ),
            'protocolsettlementtiles':    (
                'settlementTiles.*.tilePhoto.path',
            ),
            'protocolwaterqualities':     tuple(),
        }

        for e in expeditions:
            try:
                if 'siteCondition' in e['protocols'] and e['protocols']['siteCondition']:
                    protoTables['protocolsiteconditions'].add(
                        e['protocols']['siteCondition']
                    )

                if 'oysterMeasurement' in e['protocols'] and e['protocols']['oysterMeasurement']:
                    protoTables['protocoloystermeasurements'].add(
                        e['protocols']['oysterMeasurement']
                    )

                if 'mobileTrap' in e['protocols'] and e['protocols']['mobileTrap']:
                    protoTables['protocolmobiletraps'].add(
                        e['protocols']['mobileTrap']
                    )

                if 'settlementTiles' in e['protocols'] and e['protocols']['settlementTiles']:
                    protoTables['protocolsettlementtiles'].add(
                        e['protocols']['settlementTiles']
                    )

                if 'waterQuality' in e['protocols'] and e['protocols']['waterQuality']:
                    protoTables['protocolwaterqualities'].add(
                        e['protocols']['waterQuality']
                    )

            except KeyError:
                continue

        for table, idset in protoTables.items():
            if len(idset):
                for record in self.client.collection(table).query(
                    '_id/{}'.format('|'.join(list(idset))),
                    limit=False
                ):
                    for field in protoImageFields[table]:
                        try:
                            values = dpath.util.values(dict(record), field, separator='.')
                        except KeyError:
                            continue

                        for v in values:
                            images.append({
                                'from': table,
                                'url':  v,
                            })

        return jsonify(images)


class ProtocolSiteConditions(CollectionView):
    route_base      = 'protocol-site-conditions'
    collection_name = 'protocolsiteconditions'


class ProtocolOysterMeasurements(CollectionView):
    route_base      = 'protocol-oyster-measurements'
    collection_name = 'protocoloystermeasurements'


class ProtocolMobileTraps(CollectionView):
    route_base      = 'protocol-mobile-traps'
    collection_name = 'protocolmobiletraps'


class ProtocolSettlementTiles(CollectionView):
    route_base      = 'protocol-settlement-tiles'
    collection_name = 'protocolsettlementtiles'


class ProtocolWaterQualities(CollectionView):
    route_base      = 'protocol-water-qualities'
    collection_name = 'protocolwaterqualities'


class RestorationStations(GeoCollectionView):
    route_base      = 'restoration-stations'
    collection_name = 'restorationstations'
    results_only    = True

class Sites(GeoCollectionView):
    route_base      = 'sites'
    collection_name = 'sites'
    results_only    = True


class MobileOrganisms(CollectionView):
    route_base      = 'mobile-organisms'
    collection_name = 'mobileorganisms'
    results_only    = True


class SessileOrganisms(CollectionView):
    route_base      = 'sessile-organisms'
    collection_name = 'sessileorganisms'
    results_only    = True
