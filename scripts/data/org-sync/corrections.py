# flake8: noqa
import pivot
import csv
import sys
import re

client = pivot.Client()

schoolorgs = client.collection('schoolorgs')
corrections = dict()
doe = dict()

# parse the corrections file
with open('tmp/org-sync/updated-corrections.tsv', 'rU') as file:
    reader = csv.DictReader(file, dialect='excel-tab')

    for row in reader:
        key = row['BOP_ID']
        corrections[key] = row

with open('tmp/org-sync/doe-list.csv', 'rU') as file:
    reader = csv.DictReader(file, dialect='excel')

    for row in reader:
        key = row['ATS System Code']
        doe[key] = row

renames = 0

def normgrade(grade):
    grade = re.sub(r'^0', '', grade).lower()

    if grade == 'pk':
        return 'pre-k'
    elif grade == 'se':
        return 'special-education'

    try:
        return int(grade)
    except ValueError:
        return grade


# for each school-org in the database...
for org in schoolorgs.query('all', limit=10000):
    org_id = org['id']

    # if this organization has a correction associated with it...
    if org_id in corrections:
        correction = corrections[ org_id ]
        correction['Org_Type'] = re.sub(
            r'[\W\s]+',
            '',
            correction['Org_Type'].strip().lower()
        )

        if correction['ATS_CODE'] == 'custom':
            print('Update {}: {}'.format(
                org_id,
                correction['BOP_NAME']
            ))

            org['name']             = correction['BOP_NAME']

            if correction['Org_Type'] == 'nonprofitcommunityorganization':
                org['organizationType'] = 'community organization'

            elif correction['Org_Type'] == 'collegeuniversity':
                org['organizationType'] = 'college'

            elif correction['Org_Type'] == 'business':
                org['organizationType'] = 'business'

            elif correction['Org_Type'] == 'governmentagency':
                org['organizationType'] = 'government'

            elif correction['Org_Type'] == 'school':
                org['organizationType'] = 'school'


            # type of school
            if correction['TYPE_OF_SCHOOL'].lower() == 'nyc public':
                org['schoolType'] = 'nyc-public'

            elif 'charter' in correction['TYPE_OF_SCHOOL'].lower():
                org['schoolType'] = 'nyc-charter'

            elif correction['TYPE_OF_SCHOOL'].lower() == 'private':
                org['schoolType'] = 'private'

            elif correction['TYPE_OF_SCHOOL'].lower() == 'other public':
                org['schoolType'] = 'other-public'

            schoolorgs.update(org)

        # if the corrected DOE name is actually set (some of these in final-corrections.tsv
        # are blank)
        elif correction['ATS_CODE'] in doe:
            doe_record = doe[correction['ATS_CODE']]

            print('Rename {}: "{}" -> "{}"'.format(
                org_id,
                org['name'],
                doe_record['Location Name']
            ))

            org['name']             = doe_record['Location Name']
            org['streetAddress']    = re.sub(r'\s+', ' ', doe_record['Primary Address'].title())
            org['city']             = doe_record['City'].title()
            org['state']            = doe_record['State Code']
            org['neighborhood']     = doe_record['NTA_Name']
            org['zip']              = doe_record['Zip']
            org['organizationType'] = 'school'
            org['syncId']           = doe_record['ATS System Code']
            org['creator']          = org.get('creator', '5707ec9277d0beb8cb1c8e19')
            org['gradeLevels']      = doe_record['Location Category Description'].strip()
            org['locationType']     = doe_record['Location Type Description']

            if doe_record['Managed By Name'] == 'DOE':
                org['schoolType'] = 'nyc-public'

            elif doe_record['Managed By Name'] == 'Charter':
                org['schoolType'] = 'nyc-charter'

            org['creator'] = org['creator'].replace('ObjectIdHex("', '')
            org['creator'] = org['creator'].replace('")', '')

            if len(doe_record['Principal Name']) > 0:
                org['principal']        = doe_record['Principal Name'].title()

            if len(doe_record['Principal Phone Number']) > 0:
                org['principalPhone']  = doe_record['Principal Phone Number']

            if len(doe_record['Community District']) > 0:
                org['communityBoard'] = doe_record['Community District']

            if len(doe_record['Council District']) > 0:
                org['district'] = doe_record['Council District']

            org['gradesTaught'] = [
                normgrade(g) for g in doe_record['Grades'].strip().lower().split(',')
            ]

            # actually save the changes to the database
            schoolorgs.update(org)

            renames += 1


print('Processed {} renames'.format(renames))
