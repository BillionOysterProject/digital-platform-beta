from __future__ import absolute_import
from __future__ import unicode_literals
import logging
import six
import unicodecsv
import io
import boto3
import re
import json
import dpath.util
from collections import OrderedDict
from .. import API, env
from ..time import Time
from ..utils import autotype

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

def calcTotalGridPoints(context, field):
    count = 0

    try:
        for tile in context['$']['protocols']['settlementTiles']['settlementTiles']:
            for k, v in tile.items():
                if k.startswith('grid'):
                    count += 1
    except KeyError:
        pass

    return count + 1

def calcTotalPerOrganismCount(context, field):
    name = context['ctx']['organism']['_id']
    count = 0

    try:
        for tile in context['$']['protocols']['settlementTiles']['settlementTiles']:
            for k, v in tile.items():
                if k.startswith('grid'):
                    try:
                        if v['organism']['_id'] == name:
                            count += 1
                    except (KeyError, TypeError):
                        continue
    except KeyError:
        pass

    return count

EXPEDITION_DATA_EXPORT_FIELDS = [{
    'field': 'id',
    'label': 'Expedition ID',
}, {
    'field': 'monitoringStartDate',
    'label': 'Date-Time',
}, {
    'field': 'station.site.name',
    'label': 'Site Name',
}, {
    'field': 'station.site.boroughCounty',
    'label': 'Site Borough/City',
}, {
    'field': 'station.site.bodyOfWater',
    'label': 'Body of Water'
}, {
    'field': 'station.name',
    'label': 'Structure Name',
}, {
    'field': 'station.structureType',
    'label': 'Structure Type',
}, {
    'field': 'team.schoolOrg.name',
    'label': 'Organization'
}, {
    'field': 'team.schoolOrg.city',
    'label': 'Organization Borough/City'
}, {
    'field': 'adultCount',
    'label': 'Number of adults',
}, {
    'field': 'childCount',
    'label': 'Number of students',
}, {
    'field': 'notes',
    'label': 'Expedition Notes',
}, {
    'field': 'protocols.oysterMeasurement.conditionOfOysterCage.bioaccumulationOnCage',
    'label': 'Bioaccumulation on cage',
    'only': [ 'expeditions', 'oyster-measurements' ],
}, {
    'field': 'protocols.oysterMeasurement.measuringOysterGrowth.substrateShells.*.measurements.*.sizeOfLiveOysterMM',
    'label': 'Oyster Measurement {j:02d} (mm)',
    'only': [ 'expeditions', 'oyster-measurements' ],
}, {
    'field': 'protocols.oysterMeasurement.notes',
    'label': 'Oyster Measurement Notes',
    'only': [ 'expeditions', 'oyster-measurements' ],
}, {
    'field': 'protocols.siteCondition.meteorologicalConditions.weatherConditions',
    'label': 'Weather',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.siteCondition.meteorologicalConditions.airTemperatureC',
    'label': 'Air Temperature (°C)',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.siteCondition.meteorologicalConditions.windSpeedMPH',
    'label': 'Wind speed (mph)',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.siteCondition.meteorologicalConditions.windDirection',
    'label': 'Wind direction',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.siteCondition.recentRainfall.rainedIn7Days',
    'label': 'Rained in the past 7 days',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.siteCondition.recentRainfall.rainedIn72Hours',
    'label': 'Rained in the past 72 hours',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.siteCondition.recentRainfall.rainedIn24Hours',
    'label': 'Rained in the past 24 hours',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.siteCondition.waterConditions.waterColor',
    'label': 'Water color',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.siteCondition.waterConditions.oilSheen',
    'label': 'Oil sheen present',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.siteCondition.waterConditions.garbage.garbagePresent',
    'label': 'Garbage in water',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.siteCondition.waterConditions.markedCombinedSewerOverflowPipes.markedCSOPresent',
    'label': 'Combined Sewer Overflow present',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.siteCondition.waterConditions.markedCombinedSewerOverflowPipes.howMuchFlowThrough',
    'label': 'Combined Sewer Overflow flow',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.siteCondition.notes',
    'label': 'Site Conditions Notes',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.mobileTrap.mobileOrganisms.*.count',
    'label': 'Organism: {ctx[organism][commonName]}',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.mobileTrap.notes',
    'label': 'Mobile Organism Notes',
    'only': [ 'expeditions' ],
}, {
    'label': 'Total # of Grid Points',
    'value': calcTotalGridPoints,
    'only': [ 'expeditions' ],
},

# {
#     'field': 'protocols.settlementTiles.settlementTiles.*.grid*.organism.commonName',
#     'label': '# of Grid Pts: {ctx[organism][commonName]}',
#     'value': calcTotalPerOrganismCount,
# },

{
    'field': 'protocols.settlementTiles.settlementTiles.*.grid*.organism.commonName',
    'label': 'Tile {i:02d}, Grid Pt. {j:02d}',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.settlementTiles.notes',
    'label': 'Sessile Organism Notes',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.waterQuality.samples.*.waterTemperature.method',
    'label': 'Sample {i:02d}: Water Temperature Method',
    'group': 'samples',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.waterQuality.samples.*.waterTemperature.results.0',
    'label': 'Sample {i:02d}: Water Temperature (Result 1)',
    'group': 'samples',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.waterQuality.samples.*.waterTemperature.results.1',
    'label': 'Sample {i:02d}: Water Temperature (Result 2)',
    'group': 'samples',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.waterQuality.samples.*.waterTemperature.results.2',
    'label': 'Sample {i:02d}: Water Temperature (Result 3)',
    'group': 'samples',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.waterQuality.samples.*.dissolvedOxygen.method',
    'label': 'Sample {i:02d}: Dissolved Oxygen Method',
    'group': 'samples',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.waterQuality.samples.*.dissolvedOxygen.results.0',
    'label': 'Sample {i:02d}: Dissolved Oxygen (Result 1)',
    'group': 'samples',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.waterQuality.samples.*.dissolvedOxygen.results.1',
    'label': 'Sample {i:02d}: Dissolved Oxygen (Result 2)',
    'group': 'samples',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.waterQuality.samples.*.dissolvedOxygen.results.2',
    'label': 'Sample {i:02d}: Dissolved Oxygen (Result 3)',
    'group': 'samples',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.waterQuality.samples.*.salinity.method',
    'label': 'Sample {i:02d}: Salinity Method',
    'group': 'samples',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.waterQuality.samples.*.salinity.results.0',
    'label': 'Sample {i:02d}: Salinity (Result 1)',
    'group': 'samples',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.waterQuality.samples.*.salinity.results.1',
    'label': 'Sample {i:02d}: Salinity (Result 2)',
    'group': 'samples',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.waterQuality.samples.*.salinity.results.2',
    'label': 'Sample {i:02d}: Salinity (Result 3)',
    'group': 'samples',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.waterQuality.samples.*.pH.method',
    'label': 'Sample {i:02d}: pH Method',
    'group': 'samples',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.waterQuality.samples.*.pH.results.0',
    'label': 'Sample {i:02d}: pH (Result 1)',
    'group': 'samples',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.waterQuality.samples.*.pH.results.1',
    'label': 'Sample {i:02d}: pH (Result 2)',
    'group': 'samples',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.waterQuality.samples.*.pH.results.2',
    'label': 'Sample {i:02d}: pH (Result 3)',
    'group': 'samples',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.waterQuality.samples.*.turbidity.method',
    'label': 'Sample {i:02d}: Turbidity Method',
    'group': 'samples',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.waterQuality.samples.*.turbidity.results.0',
    'label': 'Sample {i:02d}: Turbidity (Result 1)',
    'group': 'samples',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.waterQuality.samples.*.turbidity.results.1',
    'label': 'Sample {i:02d}: Turbidity (Result 2)',
    'group': 'samples',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.waterQuality.samples.*.turbidity.results.2',
    'label': 'Sample {i:02d}: Turbidity (Result 3)',
    'group': 'samples',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.waterQuality.samples.*.ammonia.method',
    'label': 'Sample {i:02d}: Ammonia Method',
    'group': 'samples',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.waterQuality.samples.*.ammonia.results.0',
    'label': 'Sample {i:02d}: Ammonia (Result 1)',
    'group': 'samples',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.waterQuality.samples.*.ammonia.results.1',
    'label': 'Sample {i:02d}: Ammonia (Result 2)',
    'group': 'samples',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.waterQuality.samples.*.ammonia.results.2',
    'label': 'Sample {i:02d}: Ammonia (Result 3)',
    'group': 'samples',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.waterQuality.samples.*.nitrates.method',
    'label': 'Sample {i:02d}: Nitrates Method',
    'group': 'samples',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.waterQuality.samples.*.nitrates.results.0',
    'label': 'Sample {i:02d}: Nitrates (Result 1)',
    'group': 'samples',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.waterQuality.samples.*.nitrates.results.1',
    'label': 'Sample {i:02d}: Nitrates (Result 2)',
    'group': 'samples',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.waterQuality.samples.*.nitrates.results.2',
    'label': 'Sample {i:02d}: Nitrates (Result 3)',
    'group': 'samples',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.waterQuality.samples.*.phosphate.method',
    'label': 'Sample {i:02d}: Phosphate Method',
    'group': 'samples',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.waterQuality.samples.*.phosphate.results.0',
    'label': 'Sample {i:02d}: Phosphate (Result 1)',
    'group': 'samples',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.waterQuality.samples.*.phosphate.results.1',
    'label': 'Sample {i:02d}: Phosphate (Result 2)',
    'group': 'samples',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.waterQuality.samples.*.phosphate.results.2',
    'label': 'Sample {i:02d}: Phosphate (Result 3)',
    'group': 'samples',
    'only': [ 'expeditions' ],
}, {
    'field': 'protocols.waterQuality.notes',
    'label': 'Water Quality Notes',
    'only': [ 'expeditions' ],
}]


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


def populate_expedition_record(record, source, flt, counter=0, placeholders={}, pos=0):
    # if 'field' not in flt or not len(flt['field']):
    #     return

    if 'field' in flt:
        keypath = flt['field'].split('.')
    else:
        keypath = []

    current = source

    # print('{} -> {}'.format(flt.get('parents', ''), keypath))

    if '$' not in placeholders:
        placeholders['$'] = current

    if 'ctx' in flt:
        placeholders['ctx'] = flt['ctx']

    # work our way down to the data we're trying to add
    for i, segment in enumerate(keypath):
        if '*' in segment:
            if isinstance(current, list):
                for subi, subl in enumerate(current):
                    subph = placeholders.copy()
                    subph[chr(105 + counter)] = int(subi) + 1

                    subflt = {
                        'field':   '.'.join(keypath[(i + 1):]),
                        'label':   flt['label'],
                        'value':   flt.get('value'),
                        'ctx':     subl,
                        'parents': keypath[:i],
                    }

                    # print('{}{} counter={} kp={} data={}'.format('  ' * (counter + 1), subi, counter, list(subph.keys()), subl.__class__.__name__))
                    populate_expedition_record(record, subl, subflt, counter + 1, placeholders=subph, pos=pos)

            elif isinstance(current, dict):
                for subk, subv in current.items():
                    if segment != '*' and not re.match(segment.replace('*', '.*'), subk):
                        continue

                    subph = placeholders.copy()
                    subph[chr(105 + counter)] = autotype(subk.replace(segment.replace('*', ''), ''))

                    subflt = {
                        'field':   '.'.join(keypath[(i + 1):]),
                        'label':   flt['label'],
                        'value':   flt.get('value'),
                        'ctx':     subv,
                        'parents': keypath[:i],
                    }

                    # print('{}{} counter={} kp={} data={}'.format('  ' * (counter + 1), subk, counter, list(subph.keys()), subv.__class__.__name__))
                    populate_expedition_record(record, subv, subflt, counter + 1, placeholders=subph, pos=pos)

            return

        elif isinstance(current, list):
            try:
                current = current[int(segment)]
            except IndexError:
                current = None
                break

        elif isinstance(current, dict):
            if segment in current:
                current = current[segment]
            else:
                current = None
                break
        else:
            current = None
            break

    try:
        lbl = flt['label'].format(**placeholders)
    except (KeyError, TypeError):
        return

    if 'value' in flt:
        if callable(flt['value']):
            current = flt['value'](placeholders, flt)
        elif isinstance(flt['value'], six.string_types):
            current = flt['value'].format(**placeholders)
        elif flt['value'] is not None:
            current = flt['value']

    record['{:04d}|{}'.format(pos, lbl)] = current


def generate_batch_expeditions_tsv(report_name='expeditions', query='status/published', limit=False, maxcount=-1, sort_by='monitoringStartDate'):
    api = API('bop-worker')
    api.setup()
    s3 = boto3.client('s3')

    bucket = env.get_reports_bucket()
    s3.head_bucket(Bucket=bucket)

    data = OrderedDict()
    fullFieldSet = set()
    pageSize = (limit or 25)
    offset = 0
    count = 0

    while maxcount < 0 or count < maxcount:
        expeditions = api.db.collection('expeditions').query(
            query,
            limit=pageSize,
            offset=offset,
            sort=['monitoringStartDate']
        )

        if len(expeditions) == 0:
            break
        else:
            offset += len(expeditions)

        for expedition in expeditions:
            record = OrderedDict()
            count += 1
            pos = 0
            lastgroup = None

            for i, flt in enumerate(EXPEDITION_DATA_EXPORT_FIELDS):
                # the "only" list being present means that only report_names in that
                # list will cause those field(s) to be included
                #
                # the "only" list being absent means that the field(s) should be included
                # in all cases
                #
                if 'only' in flt:
                    if report_name not in flt['only']:
                        continue

                # only advance the position counter across distinct group boundaries
                if 'group' not in flt or flt.get('group') is not lastgroup:
                    pos += 1

                populate_expedition_record(record, dict(expedition), flt, pos=pos)

                lastgroup = flt.get('group')


            data[expedition['name']] = record

            for field in record.keys():
                fullFieldSet.add(field)

    output = io.BytesIO()
    writer = unicodecsv.writer(
        output,
        dialect='excel-tab'
    )

    # get the final output order that the columns should be in by sorting by the desired field
    sortkey = ''

    for i, flt in enumerate(EXPEDITION_DATA_EXPORT_FIELDS):
        if flt.get('field') == sort_by:
            sortkey = '{:04d}|{}'.format(i+1, flt.get('label'))

    if not len(sortkey):
        raise Exception("Cannot find sort key field {}", sort_by)

    data = OrderedDict(
        sorted(data.items(), key=lambda d: d[1].get(sortkey))
    )

    orderedExpNames = data.keys()

    # write header
    writer.writerow(['Datum'] + list(orderedExpNames))

    for field in sorted(fullFieldSet):
        lbl = field.split('|')[-1]
        row = [lbl]

        for expname in data.keys():
            try:
                row.append(data[expname][field])
            except KeyError:
                row.append('')

        writer.writerow(row)

    output.seek(0)

    # upload the exported file, overwriting the existing copy
    s3.put_object(
        ACL='public-read',
        Bucket=bucket,
        Key='{}/{}.tsv'.format('reports', report_name),
        ContentType='text/tab-separated-values',
        StorageClass='REDUCED_REDUNDANCY',
        Body=output,
        Metadata={
            'GeneratedAt': '{}'.format(Time()),
        },
    )
