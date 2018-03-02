import pivot
import csv
import re
from difflib import SequenceMatcher

rxNormalize = re.compile('[\s\_\-\.]')

client = pivot.Client()
orgs = client.collection('schoolorgs')
doe = list()
nycod = list()
heather = list()


def thundernormalizer(name):
    name = rxNormalize.sub('', name)
    name = name.replace(' IX',  '9', 1)
    name = name.replace(' VII', '8', 1)
    name = name.replace(' VI',  '7', 1)
    name = name.replace(' VI',  '6', 1)
    name = name.replace(' V',   '5', 1)
    name = name.replace(' IV',  '4', 1)
    name = name.replace(' III', '3', 1)
    name = name.replace(' II',  '2', 1)
    name = name.replace(' I',   '1', 1)
    name = name.replace('PSIS', 'P.S./I.S.', 1)

    name = name.upper()

    return '{}'.format(name)


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

with open('tmp/org-sync/doe-list.csv', 'rU') as file:
    reader = csv.DictReader(file, dialect='excel')

    for row in reader:
        doe.append(row)


with open('tmp/org-sync/nyc-open-data-list.tsv', 'rU') as file:
    reader = csv.DictReader(file, dialect='excel-tab')

    for row in reader:
        nycod.append(row)


with open('tmp/org-sync/what-heather-did.tsv', 'rU') as file:
    reader = csv.DictReader(file, dialect='excel-tab')

    for row in reader:
        heather.append(row)


total = 0
doe_match = 0
unmatched = list()
matches = list()

print('BOP_ID\tATS_CODE\tBOP_NAME\tDOE_NAME\tNYCOD_NAME\tALREADY_DONE\tTYPE_OF_SCHOOL\tADDRESS_1\tNEIGHBORHOOD\tCITY\tSTATE\tZIP\tCOMMUNITY_BOARD\tCOUNCIL_DISTRICT\t')

for org in orgs.query('all', limit=5000, sort=['name']):
    total += 1
    platform_name = thundernormalizer(org.name)
    doe_record = None
    nycod_record = {}
    potentials = {}
    nycod_potentials = {}
    is_exact = False
    heather_did_this = False

    for doe_org in doe:
        doe_location = thundernormalizer(doe_org['Location Name'])

        if doe_location == platform_name:
            doe_record = doe_org
            is_exact = True
            break
        else:
            doe_ps = re.match('([PI]S\d+)', doe_location)
            dp_ps = re.match('([PI]S\d+)', platform_name)

            if doe_ps and dp_ps:
                if doe_ps.group(1) == dp_ps.group(1):
                    doe_record = doe_org
                    break

            ratio = similar(doe_location, platform_name)

            if ratio > 0.8:
                potentials[ratio] = doe_org

    for nycod_org in nycod:
        nycod_location = thundernormalizer(nycod_org['LOCATION_NAME'])

        if nycod_location == platform_name:
            nycod_record = nycod_org
            is_exact = True
            break
        else:
            nycod_ps = re.match('([PI]S\d+)', nycod_location)
            dp_ps = re.match('([PI]S\d+)', platform_name)

            if nycod_ps and dp_ps:
                if nycod_ps.group(1) == dp_ps.group(1):
                    nycod_record = nycod_org
                    break

            ratio = similar(nycod_location, platform_name)

            if ratio > 0.8:
                nycod_potentials[ratio] = nycod_org

    if len(potentials):
        max_score = list(reversed(sorted(potentials.keys())))[0]
        doe_record = potentials[max_score]

    if len(nycod_potentials):
        max_score = list(reversed(sorted(nycod_potentials.keys())))[0]
        nycod_record = nycod_potentials[max_score]

    if isinstance(doe_record, dict):
        for heather_org in heather:
            if heather_org['Official DOE Name'] == doe_record.get('Location Name'):
                heather_did_this = True

        managed_by = doe_record.get('Managed By Name')

        if managed_by == 'DOE':
            managed_by = 'NYC Public'

        print('\t'.join([
            org.id,
            doe_record.get('ATS System Code', ''),
            org.name,
            doe_record.get('Location Name', ''),
            nycod_record.get('LOCATION_NAME', ''),
            ('yes' if heather_did_this else 'no'),
            managed_by,
            doe_record.get('Primary Address', ''),
            doe_record.get('NTA_Name', ''),
            doe_record.get('City', ''),
            doe_record.get('State Code', ''),
            doe_record.get('Zip', ''),
            doe_record.get('Community District', ''),
            doe_record.get('Council District', ''),
            doe_record.get('Principal Name', ''),
            doe_record.get('Principal Phone Number', ''),
        ]))
    else:
        print('\t'.join([
            org.id,
            '',
            org.name,
            '',
            nycod_record.get('LOCATION_NAME', ''),
            'unsure',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
        ]))
