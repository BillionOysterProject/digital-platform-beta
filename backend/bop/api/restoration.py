from __future__ import absolute_import
from __future__ import unicode_literals
from .endpoints import CollectionView
from flask import Response, jsonify
from flask_classy import route
import requests
import io
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

    expand_fields   = {
        'teamLead': (
            'users', ['_id', 'displayName', 'username', 'profileImageURL'],
        ),
        'team': (
            'teams', ['_id', 'name', 'schoolOrg'],
        ),
        'team.schoolOrg': (
            'schoolorgs', ['_id', 'name'],
        ),
        'station': (
            'restorationstations', ['_id', 'name'],
        ),
        'teamLists.mobileTrap': (
            'users', ['_id', 'displyaName', 'username', 'profileImageURL'],
        ),
        'teamLists.oysterMeasurement': (
            'users', ['_id', 'displayName', 'username', 'profileImageURL'],
        ),
        'teamLists.settlementTiles': (
            'users', ['_id', 'displayName', 'username', 'profileImageURL'],
        ),
        'teamLists.siteCondition': (
            'users', ['_id', 'displayName', 'username', 'profileImageURL'],
        ),
        'teamLists.waterQuality': (
            'users', ['_id', 'displayName', 'username', 'profileImageURL'],
        ),
        'protocols.mobileTrap': (
            'protocolmobiletraps', [],
        ),
        'protocols.oysterMeasurement': (
            'protocoloystermeasurements', [],
        ),
        'protocols.settlementTiles': (
            'protocolsettlementtiles', [],
        ),
        'protocols.siteCondition': (
            'protocolsiteconditions', [],
        ),
        'protocols.waterQuality': (
            'protocolwaterqualities', [],
        ),
    }

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


class RestorationStations(CollectionView):
    route_base      = 'restoration-stations'
    collection_name = 'restorationstations'
    results_only    = True

    expand_fields   = {
        'schoolOrg': (
            'schoolorgs', ['_id', 'name'],
        ),

        'teamLead': (
            'users', ['_id', 'displayName', 'username'],
        ),
    }


class Sites(CollectionView):
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
