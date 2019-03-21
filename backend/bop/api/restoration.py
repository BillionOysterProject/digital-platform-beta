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
import six
from .auth import Teams
from .. import env
from ..time import Time
from ..utils import dict_merge, compact, mutate_dict, autotype
import unicodecsv
from sortedcontainers import SortedList


class Skip(Exception):
    pass


class ExpeditionActivities(CollectionView):
    route_base      = 'expedition-activities'
    collection_name = 'expeditionactivities'
    results_only    = True


class Batches(CollectionView):
    route_base      = 'batches'
    collection_name = 'batches'


class Organisms(CollectionView):
    @classmethod
    def first_by_name(cls, commonOrLatin):
        try:
            results = cls.get_collection().query(
                'latinName/like:{}/commonName/like:{}'.format(commonOrLatin, commonOrLatin),
                conjunction='or'
            )

            if len(results):
                return results[0]
        except:
            logging.exception('first_by_name:')
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
            noexpand=True
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
        flatBody = request.form or json.loads(request.get_data(as_text=True))
        flatBody = mutate_dict(flatBody, valueFn=lambda v: autotype(v))

        body = {}
        expedition = None
        station = None
        team = None

        for k, v in flatBody.items():
            dpath.util.new(body, k, v, separator='.')

        subclass = {
            'siteCondition':     ProtocolSiteConditions,
            'oysterMeasurement': ProtocolOysterMeasurements,
            'settlementTiles':   ProtocolSettlementTiles,
            'mobileTrap':        ProtocolMobileTraps,
            'waterQuality':      ProtocolWaterQualities,
        }

        # load any existing expedition
        if '_id' in body:
            expedition = Expeditions.get_collection().get(body['_id'], noexpand=True)
            station = expedition['station']
        else:
            expedition = {}

        # figure out which station this expedition belongs to
        if flatBody.get('station._id'):
            station = flatBody.get('station._id')
        elif flatBody.get('station.name'):
            try:
                station = RestorationStations.first_by_name(flatBody.get('station.name')).id
            except:
                return 'Must specify an Oyster Research Station for this expedition', 400

        # figure out which team this expedition belongs to
        if flatBody.get('team._id'):
            team = flatBody.get('team._id')
        elif flatBody.get('team.name'):
            try:
                team = Teams.first_by_name(flatBody.get('team.name')).id
            except:
                return 'Must specify a team for this expedition', 400

        dateTime = '{}T{}'.format(body.get('monitoringStartDateDate'), body.get('monitoringStartDateTime'))

        expedition.update(compact({
            'name'               : body.get('name'),
            'notes'              : body.get('notes'),
            'station'            : station,
            'status'             : body.get('status'),
            'monitoringStartDate': dateTime,
            'monitoringEndDate'  : dateTime,
            'adultCount'         : body.get('adultCount'),
            'childCount'         : body.get('childCount'),
            'team'               : team,
            'protocols'          : {},
        }))

        if 'teamLead' not in body:
            user = self.current_user

            if user.has_any_role('admin', 'team-lead'):
                expedition['teamLead'] = user.get_id()
            elif expedition['station']:
                try:
                    station = RestorationStations.get_collection().get(expedition['station'])

                    if 'teamLead' in station:
                        expedition['teamLead'] = station['team']['_id']
                except:
                    pass

            if 'teamLists' in body:
                expedition['teamLists'] = body.get('teamLists', [])

            if 'teamLists' in expedition:
                lists = expedition['teamLists']

                for protocol, members in lists.items():
                    lists[protocol] = list(set([
                        m for m in members if isinstance(m, six.string_types)
                    ]))

                expedition['teamLists'] = lists

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
                            try:
                                subrecord, created = subclass[name].record_from_submit(
                                    body['protocols'][name]
                                )
                            except Skip:
                                continue

                            expedition['protocols'][name] = subrecord.get('id')

                            # if expedition.get('status') is 'published':
                            #     expedition['protocols'][name]['status'] = 'published'
                            # else:
                            #     expedition['protocols'][name]['status'] = 'published'

                            # TODO: temp, remove this in favor of the line above
                            #expedition['protocols'][name] = subrecord

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

        # WRITE
        try:
            expedition = self.get_collection().update_or_create(expedition).records[0]
        except IndexError:
            pass

        return jsonify(expedition)


class ProtocolSiteConditions(CollectionView):
    route_base      = 'protocol-site-conditions'
    collection_name = 'protocolsiteconditions'

    @classmethod
    def record_from_submit(cls, body):
        return cls.save(body)


class ProtocolOysterMeasurements(CollectionView):
    route_base      = 'protocol-oyster-measurements'
    collection_name = 'protocoloystermeasurements'

    @classmethod
    def record_from_submit(cls, body):
        _id = body.get('_id')

        if _id:
            record = cls.get_collection().get(_id)
        else:
            record = {}

        observations = body.pop('observations', [])

        # reject null observations
        if 'measuringOysterGrowth' in record and isinstance(record['measuringOysterGrowth'], dict):
            record['measuringOysterGrowth']['substrateShells'] = []

        if len(observations):
            for pair in observations:
                if len(pair) == 2:
                    shellNumber = pair[0]
                    mm = pair[1]

                    if shellNumber and mm:
                        dict_merge(record, cls.append_oyster_measurement(record, shellNumber, mm))

            record.update(body)

        return cls.save(record)

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
        _id = body.get('_id')

        if _id:
            record = cls.get_collection().get(_id)
        else:
            record = {}

        record['notes'] = body.get('notes')
        organisms = body.pop('mobileOrganisms', [])

        if len(organisms):
            neworgs = []

            for pair in organisms:
                if len(pair) >= 2 and pair[0] and pair[1]:
                    commonOrLatin = pair[0]
                    count = int(pair[1])

                    mobileOrganism = MobileOrganisms.first_by_name(commonOrLatin)

                    if mobileOrganism:
                        neworgs.append({
                            'count': count,
                            'organism': mobileOrganism.id,
                            'notesQuestions': None,
                            'sketchPhoto': {
                                'path': '',
                            },
                        })

            record['mobileOrganisms'] = neworgs

        return cls.save(record)


class ProtocolSettlementTiles(CollectionView):
    route_base      = 'protocol-settlement-tiles'
    collection_name = 'protocolsettlementtiles'

    @classmethod
    def record_from_submit(cls, body):
        _id = body.get('_id')

        if _id:
            record = cls.get_collection().get(_id)
        else:
            record = {}

        record['notes'] = body.get('notes')
        grids = body.pop('settlementTiles', [])

        # junky "cache"
        organisms = {}

        if len(grids):
            # get the total number of populated tiles in the submitted data
            tileCount = max([
                len([
                    i for i in t if i is not None and i.lower() != 'n/a'
                ]) for t in grids
            ])

            # build that many empty settlement tiles
            record['settlementTiles'] = [cls.make_empty_tile(i) for i in range(tileCount)]

            # for each grid square...
            for i, grid in enumerate(grids):
                tileToSave = {}

                # for each tile...
                for j, commonOrLatin in enumerate(grid):
                    try:
                        if not commonOrLatin:
                            continue

                        sessileOrganism = None

                        if commonOrLatin.lower() == 'n/a':
                            continue
                        elif commonOrLatin in organisms:
                            sessileOrganism = organisms[commonOrLatin]
                        else:
                            sessileOrganism = SessileOrganisms.first_by_name(commonOrLatin)

                        if sessileOrganism:
                            organisms[commonOrLatin] = sessileOrganism
                            record['settlementTiles'][j]['grid{}'.format(i+1)] = {
                                'organism': sessileOrganism.id,
                                'notes':    '',
                            }
                    except IndexError:
                        continue

            record['settlementTiles'].append(tileToSave)

        return cls.save(record)

    @classmethod
    def make_empty_tile(cls, n):
        return {
            'grid1': {},
            'grid2': {},
            'grid3': {},
            'grid4': {},
            'grid5': {},
            'grid6': {},
            'grid7': {},
            'grid8': {},
            'grid9': {},
            'grid10': {},
            'grid11': {},
            'grid12': {},
            'grid13': {},
            'grid14': {},
            'grid15': {},
            'grid16': {},
            'grid17': {},
            'grid18': {},
            'grid19': {},
            'grid20': {},
            'grid21': {},
            'grid22': {},
            'grid23': {},
            'grid24': {},
            'grid25': {},
            'tilePhoto': {},
        }


class ProtocolWaterQualities(CollectionView):
    route_base      = 'protocol-water-qualities'
    collection_name = 'protocolwaterqualities'

    @classmethod
    def record_from_submit(cls, body):
        _id = body.get('_id')
        print(json.dumps(body, indent=4))

        if _id:
            record = cls.get_collection().get(_id)
        else:
            record = {}

        # for the time being, we're only going to accept one water quality
        # sample suite per expedition
        record['notes'] = body.pop('notes', None)

        if not len(record.get('samples', [])):
            record['samples'] = []

        for index, data in body.pop('samples', {}).items():
            i = int(index)

            if i < len(record['samples']):
                sample = record['samples'][i]
            else:
                sample = {}

            sample['depthOfWaterSampleM'] = data.pop('depthOfWaterSampleM', None)

            for parameter, measurement in data.items():
                if isinstance(measurement, dict):
                    m1 = measurement.get('result1', 0)
                    m2 = measurement.get('result2', 0)
                    m3 = measurement.get('result3', 0)

                    if m1 or m2 or m3:
                        sample[parameter] = {
                            'method': measurement.get('method'),
                            'units':  measurement.get('units'),
                            'results': [m1, m2, m3],
                        }

                        sample[parameter]['average'] = float(sum(sample[parameter]['results'])) / float(len(sample[parameter]['results']))

            if i < len(record['samples']):
                record['samples'][i] = sample
            else:
                record['samples'].append(sample)

        return cls.save(record)


class RestorationStations(GeoCollectionView):
    route_base      = 'restoration-stations'
    collection_name = 'restorationstations'
    results_only    = True


class Sites(GeoCollectionView):
    route_base      = 'sites'
    collection_name = 'sites'
    results_only    = True
