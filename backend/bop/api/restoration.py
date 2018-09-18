from __future__ import absolute_import
from __future__ import unicode_literals
from .endpoints import CollectionView, GeoCollectionView
from flask import Response, jsonify, request
from flask_classy import route
import requests
import dpath.util
import io
import logging
import json
from .. import env
from ..time import Time
from ..utils import dict_merge
import unicodecsv
from sortedcontainers import SortedList


class ExpeditionActivities(CollectionView):
    route_base      = 'expedition-activities'
    collection_name = 'expeditionactivities'
    results_only    = True


class Organisms(CollectionView):
    @classmethod
    def first_by_name(cls, commonOrLatin):
        try:
            results = cls.query(
                'commonName/is:{}/latinName/is:{}'.format(commonOrLatin, commonOrLatin),
                conjunction='or'
            )

            if len(results) == 1:
                return results[0]
        except:
            pass

        return None


class MobileOrganisms(Organisms):
    route_base      = 'mobile-organisms'
    collection_name = 'mobileorganisms'
    results_only    = True


class SessileOrganisms(Organisms):
    route_base      = 'sessile-organisms'
    collection_name = 'sessileorganisms'
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

    def post(self):
        flatBody = request.form or request.json
        body = {}


        for k, v in flatBody.items():
            dpath.util.new(body, k, v, separator='.')

        subclass = {
            'siteCondition':     ProtocolSiteConditions,
            'oysterMeasurement': ProtocolOysterMeasurements,
            'settlementTiles':   ProtocolSettlementTiles,
            'mobileTrap':        ProtocolMobileTraps,
            'waterQuality':      ProtocolWaterQualities,
        }

        expedition = {
            'protocols': {},
        }

        return jsonify(body)

        if 'protocols' in body:
            # for each protocol, delegate processing that protocol's data to its
            # own class-specific implementation.
            #
            # The record_from_submit() function will return the record
            # that should be saved on the expedition, or raise a validation error.
            #
            for name, protocol in body['protocols'].items():
                creates = {}

                try:
                    if name in subclass:
                        if isinstance(protocol, dict):
                            subrecord, created = subclass[name].record_from_submit(
                                body['protocols'][name]
                            )

                            # expedition['protocols'][name] = subrecord.get('_id')

                            # TODO: temp, remove this in favor of the line above
                            expedition['protocols'][name] = subrecord

                            if created:
                                creates[name] = expedition['protocols'][name]
                except:
                    # if anything went wrong, cleanup the partially-created records
                    for name, record in creates.items():
                        try:
                            if name in subclass:
                                logging.warning('Cleaning up protocol {} record {}'.format(
                                    name,
                                    record
                                ))

                                subclass[name].collection.delete(record)
                        except:
                            continue

                    raise

            # cleanup the data we've processed from the input
            del body['protocols']

        # TODO: team lists
        # TODO: station
        # TODO: team
        # TODO: teamLead (current user)

        # cls.get_collection().update(expedition)

        return jsonify(expedition)


class ProtocolSiteConditions(CollectionView):
    route_base      = 'protocol-site-conditions'
    collection_name = 'protocolsiteconditions'

    @classmethod
    def record_from_submit(cls, body):
        create = (False if '_id' in body else True)
        _id = body.get('_id')

        if _id:
            record = cls.get_collection().get(_id)
        else:
            record = {}

        record.update(body)
        record = cls.get_collection().update(record)

        return record, create


class ProtocolOysterMeasurements(CollectionView):
    route_base      = 'protocol-oyster-measurements'
    collection_name = 'protocoloystermeasurements'

    @classmethod
    def record_from_submit(cls, body):
        create = (False if '_id' in body else True)
        _id = body.get('_id')

        if _id:
            record = cls.get_collection().get(_id)
        else:
            record = {}

        observations = body.pop('observations', [])

        for pair in observations:
            if len(pair) == 2:
                shellNumber = pair[0]
                mm = pair[1]

                if shellNumber and mm:
                    dict_merge(record, cls.append_oyster_measurement(record, shellNumber, mm))

        record.update(body)
        # record = cls.get_collection().update(record)

        return record, create

    @classmethod
    def append_oyster_measurement(cls, record, shellNumber, mm):
        if 'measuringOysterGrowth' not in record:
            record['measuringOysterGrowth'] = {}

        if 'substrateShells' not in record['measuringOysterGrowth']:
            record['measuringOysterGrowth']['substrateShells'] = []

        targetShell = None
        targetShellIndex = None

        for i, shell in enumerate(record['measuringOysterGrowth']['substrateShells']):
            if int(shellNumber) == int(shell['substrateShellNumber']):
                targetShellIndex = i
                targetShell = shell
                break

        if not targetShell:
            targetShell = {
                'minimumSizeOfLiveOysters': 0,
                'averageSizeOfLiveOysters': 0,
                'maximumSizeOfLiveOysters': 0,
                'measurements': [],
                'innerSidePhoto': {},
                'outerSidePhoto': {},
                'setDate': Time().isoformat(),
                'source': None,
                'substrateShellNumber': shellNumber,
                'totalNumberOfLiveOystersOnShell': 0,
            }

        targetShell['measurements'].append({
            'sizeOfLiveOysterMM': mm,
        })

        dict_merge(targetShell, cls.recalculate_shell_stats(targetShell))

        if targetShellIndex is None:
            record['measuringOysterGrowth']['substrateShells'].append(targetShell)
        else:
            record['measuringOysterGrowth']['substrateShells'][targetShellIndex] = targetShell

        return record

    @classmethod
    def recalculate_shell_stats(cls, shell):
        szMin = shell.get('minimumSizeOfLiveOysters')
        szAvg = shell.get('averageSizeOfLiveOysters')
        szMax = shell.get('maximumSizeOfLiveOysters')
        szAll = []

        for measurement in shell.get('measurements', []):
            value = measurement.get('sizeOfLiveOysterMM')

            if value:
                szAll.append(value)

                if not szMin or value < szMin:
                    szMin = value

                if not szMax or value > szMax:
                    szMax = value

        szAvg = float(sum(szAll)) / len(szAll)

        shell['minimumSizeOfLiveOysters']        = szMin
        shell['averageSizeOfLiveOysters']        = szAvg
        shell['maximumSizeOfLiveOysters']        = szMax
        shell['totalNumberOfLiveOystersOnShell'] = len(szAll)

        return shell


class ProtocolMobileTraps(CollectionView):
    route_base      = 'protocol-mobile-traps'
    collection_name = 'protocolmobiletraps'

    @classmethod
    def record_from_submit(cls, body):
        create = (False if '_id' in body else True)
        _id = body.get('_id')

        if _id:
            record = cls.get_collection().get(_id)
        else:
            record = {}

        organisms = body.pop('mobileOrganisms', [])
        record['mobileOrganisms'] = []

        for pair in organisms:
            if len(pair) >= 2:
                commonOrLatin = pair[0]
                count = int(pair[1])

                mo = MobileOrganisms.first_by_name(commonOrLatin)

                if mo:
                    record['mobileOrganisms'].append({
                    'count': count,
                    'organism': mo._id,
                    'notesQuestions': None,
                    'sketchPhoto': {
                        'path': '',
                    },
                })

        return record, create

class ProtocolSettlementTiles(CollectionView):
    route_base      = 'protocol-settlement-tiles'
    collection_name = 'protocolsettlementtiles'

    @classmethod
    def record_from_submit(cls, body):
        create = (False if '_id' in body else True)
        _id = body.get('_id')

        if _id:
            record = cls.get_collection().get(_id)
        else:
            record = {}

        tiles = body.pop('settlementTiles', [])
        record['settlementTiles'] = []

        for tile in tiles:
            tileToSave = {
                'description': tile.get('description')
            }

            for j, grid in enumerate(tile['grids']):
                if len(grid):
                    commonOrLatin = grid[0]
                    mo = SessileOrganisms.first_by_name(commonOrLatin)
                    notes = ''

                    if len(grid) > 1:
                        notes = grid[1]

                    if mo:
                        tileToSave['grid{}'.format(j)] = {
                            'organism': mo._id,
                            'notes': notes
                        }

            record['settlementTiles'].append(tileToSave)

        return record, create

class ProtocolWaterQualities(CollectionView):
    route_base      = 'protocol-water-qualities'
    collection_name = 'protocolwaterqualities'

    @classmethod
    def record_from_submit(cls, body):
        return body

class RestorationStations(GeoCollectionView):
    route_base      = 'restoration-stations'
    collection_name = 'restorationstations'
    results_only    = True

    expand_fields   = {
        'siteId': (
            'sites', [],
        ),
        'schoolOrg': (
            'schoolorgs', ['_id', 'name'],
        ),
        'team': (
            'teams', ['_id', 'name', 'created', 'teamLeads'],
        ),
        'teamLead': (
            'users', ['_id', 'displayName', 'username'],
        ),
    }


class Sites(GeoCollectionView):
    route_base      = 'sites'
    collection_name = 'sites'
    results_only    = True
