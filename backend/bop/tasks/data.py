from __future__ import absolute_import
from __future__ import unicode_literals
import logging
import unicodecsv
import io
import boto3
import re
import dpath.util
from collections import OrderedDict
from .. import API, env
from ..time import Time

SCHOOL_SYNC_SKIP_FIELDS = (
    'created',
    'creator',
    'description',
    'id',
    'name',
    'organizationType',
    'pending',
    'schoolType',
)

EXPEDITION_EXPORT_KEY = 'reports/expeditions-full.tsv'
EXPEDITION_DATA_EXPORT_FIELDS = [
    '_id',
    'monitoringStartDate',
    'name',
    'team.schoolOrg.name',
    'team.name',
    'station.name',
    'protocols.siteCondition.meteorologicalConditions.airTemperatureC',
    'protocols.siteCondition.meteorologicalConditions.weatherConditions',
    'protocols.siteCondition.meteorologicalConditions.windSpeedMPH',
    'protocols.siteCondition.meteorologicalConditions.windDirection',
    'protocols.siteCondition.humidity',
    'protocols.siteCondition.recentRainfall.rainedIn24Hours',
    'protocols.siteCondition.recentRainfall.rainedIn72Hours',
    'protocols.siteCondition.recentRainfall.rainedIn7Days',
    'protocols.siteCondition.tideConditions.referencePoint',
    'protocols.siteCondition.tideConditions.tidalCurrent',
    'protocols.siteCondition.tideConditions.closestHighTideHeight',
    'protocols.siteCondition.tideConditions.closestHighTide',
    'protocols.siteCondition.tideConditions.closestLowTideHeight',
    'protocols.siteCondition.tideConditions.closestLowTide',
    'protocols.siteCondition.waterConditions.surfaceCurrentSpeedMPS',
    'protocols.siteCondition.waterConditions.oilSheen',
    'protocols.siteCondition.waterConditions.garbage.garbagePresent',
    'protocols.siteCondition.pipes',
    'protocols.siteCondition.landConditions.shoreLineType',
    'protocols.siteCondition.landConditions.garbage.garbagePresent',
    'protocols.siteCondition.landConditions.shorelineSurfaceCoverEstPer.imperviousSurfacePer',
    'protocols.siteCondition.landConditions.shorelineSurfaceCoverEstPer.perviousSurfacePer',
    'protocols.siteCondition.landConditions.shorelineSurfaceCoverEstPer.vegetatedSurfacePer',
    'protocols.oysterMeasurement.depthOfOysterCage.submergedDepthofCageM',
    'protocols.oysterMeasurement.conditionOfOysterCage.bioaccumulationOnCage',
    'protocols.oysterMeasurement.conditionOfOysterCage.notesOnDamageToCage',
    'protocols.oysterMeasurement.maximumSizeOfAllLiveOysters',
    'protocols.oysterMeasurement.minimumSizeOfAllLiveOysters',
    'protocols.mobileTrap.organism',
    'protocols.settlementTiles.*.grid*.organism',
    'protocols.waterQuality.depth',
    'protocols.waterQuality.temperature',
    'protocols.waterQuality.dissolvedOxygen',
    'protocols.waterQuality.salinity',
    'protocols.waterQuality.ph',
    'protocols.waterQuality.turbidity',
    'protocols.waterQuality.ammonia',
    'protocols.waterQuality.nitrates',
    'protocols.waterQuality.other',
]


def sync_prospective_to_orgs():
    """
    Synchronizes certain fields from the "prospectiveorgs" table into the corresponding records in
    the "schoolorgs" table.  This process allows changes made to prospectiveorgs by other
    processes (e.g.: syncing from third-party data sources) to propagate to existing organizations.
    """
    instance        = API('bop-worker')
    schoolOrgs      = instance.db.collection('schoolorgs')
    prospectiveOrgs = instance.db.collection('prospectiveorgs')

    # for each school-org in the database...
    for school in schoolOrgs.query('all', limit=False):
        if school.syncId:
            has_changed = False

            prospectiveOrg = prospectiveOrgs.query('syncId/{}'.format(school.syncId), limit=1)

            for k, v in school.items():
                if k in SCHOOL_SYNC_SKIP_FIELDS:
                    continue

                if k in prospectiveOrg:
                    if school[k] != prospectiveOrg[k]:
                        has_changed = True
                        school[k] = prospectiveOrg[k]

            if has_changed:
                logging.info('Synced: {} ({})'.format(school.id, school.name))
                schoolOrgs.update(school)
            else:
                logging.info('Unchanged: {}'.format(school.id))


def generate_batch_expeditions_tsv():
    api = API('bop-worker')
    api.setup()
    s3 = boto3.client('s3')

    bucket = env.get_reports_bucket()
    s3.head_bucket(Bucket=bucket)

    data = []

    expeditions          = api.db.collection('expeditions').query(
        'status/published',
        limit=False,
        sort=['monitoringStartDate'],
        noexpand=True
    )

    teams                = dict([
        (record.id, dict(record)) for record in api.db.collection('teams').all(
            limit=False
        )
    ])

    stations             = dict([
        (record.id, dict(record)) for record in api.db.collection('restorationstations').all(
            limit=False
        )
    ])

    organizations        = dict([
        (record.id, dict(record)) for record in api.db.collection('schoolorgs').all(
            limit=False
        )
    ])

    p1siteConditions     = dict([
        (record.id, dict(record)) for record in api.db.collection('protocolsiteconditions').all(
            limit=False
        )
    ])

    p2oysterMeasurements = dict([
        (record.id, dict(record)) for record in api.db.collection('protocoloystermeasurements').all(
            limit=False
        )
    ])

    p3mobileTraps        = dict([
        (record.id, dict(record)) for record in api.db.collection('protocolmobiletraps').all(
            limit=False
        )
    ])

    p4settlementTiles    = dict([
        (record.id, dict(record)) for record in api.db.collection('protocolsettlementtiles').all(
            limit=False
        )
    ])

    p5waterQuality       = dict([
        (record.id, dict(record)) for record in api.db.collection('protocolwaterqualities').all(
            limit=False
        )
    ])

    prefixes = {
        'team':                        teams,
        'station':                     stations,
        'team.schoolOrg':              organizations,
        'protocols.siteCondition':     p1siteConditions,
        'protocols.oysterMeasurement': p2oysterMeasurements,
        'protocols.mobileTrap':        p3mobileTraps,
        'protocols.settlementTiles':   p4settlementTiles,
        'protocols.waterQuality':      p5waterQuality,
    }

    for expedition in expeditions:
        record = OrderedDict()
        expeditionDict = dict(expedition)

        for field in EXPEDITION_DATA_EXPORT_FIELDS:
            try:
                if field == '_id':
                    record['_id'] = expedition.id

                elif field == 'team.schoolOrg.name':
                    team = teams[expeditionDict['team']]
                    org = organizations[team['schoolOrg']]
                    record[field] = org['name']

                elif '.' not in field:
                    record[field] = expedition.get(field)

                else:
                    for prefix, results in prefixes.items():
                        results = prefixes[prefix]
                        trimmedPrefix = re.sub(r'^{}\.'.format(prefix), '', field)

                        if field.startswith(prefix + '.'):
                            subItemId = dpath.util.get(expeditionDict, prefix, separator='.')

                            if not subItemId:
                                subItemId = dpath.util.get(record, prefix, separator='.')

                            try:
                                nestedDataItem = results[subItemId]
                            except KeyError:
                                nestedDataItem = None

                            if not nestedDataItem:
                                nestedDataItem = {}

                            if len(nestedDataItem):
                                record[field] = dpath.util.get(
                                    nestedDataItem,
                                    trimmedPrefix,
                                    separator='.'
                                )

            except KeyError:
                pass

            if field not in record:
                record[field] = None

        data.append(record)

    output = io.BytesIO()
    writer = unicodecsv.DictWriter(
        output,
        fieldnames=EXPEDITION_DATA_EXPORT_FIELDS,
        dialect='excel-tab'
    )

    writer.writeheader()

    for record in data:
        writer.writerow(record)

    output.seek(0)

    # upload the exported file, overwriting the existing copy
    s3.put_object(
        ACL='public-read',
        Bucket=bucket,
        Key=EXPEDITION_EXPORT_KEY,
        ContentType='text/tab-separated-values',
        StorageClass='REDUCED_REDUNDANCY',
        Body=output,
        Metadata={
            'GeneratedAt': '{}'.format(Time()),
        },
    )
