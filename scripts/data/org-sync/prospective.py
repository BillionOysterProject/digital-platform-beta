# flake8: noqa
import pivot
import csv
import json
import sys
import logging
import re
import mmh3
import uuid

client = pivot.Client()

try:
    client.create_collection('prospectiveorgs')
except:
    pass

prospectiveorgs = client.collection('prospectiveorgs')

doe = list()
nycod = dict()

with open('tmp/org-sync/doe-list.csv', 'rU') as file:
    reader = csv.DictReader(file, dialect='excel')

    for row in reader:
        doe.append(row)

with open('tmp/org-sync/nyc-open-data-list.tsv', 'rU') as file:
    reader = csv.DictReader(file, dialect='excel-tab')

    for row in reader:
        key = str(row['ATS SYSTEM CODE']).strip()
        nycod[key] = row


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

for school in doe:
    try:
        org = {
            'syncId':        school['ATS System Code'],
            'name':          school['Location Name'],
            'streetAddress': re.sub(r'\s+', ' ', school['Primary Address'].title()),
            'neighborhood':  school['NTA_Name'],
            'city':          school['City'].title(),
            'state':         school['State Code'].upper(),
            'zip':           school['Zip'],
            'gradeLevels':   school['Location Category Description'].strip(),
            'locationType':  school['Location Type Description'],
            'properties':    dict([
                (k.lower().replace(' ', '_'), v) for k, v in school.items() if len(v)
            ]),
        }

        if school['Managed By Name'] == 'DOE':
            org['type'] = 'nyc-public'
        elif school['Managed By Name'] == 'Charter':
            org['type'] = 'nyc-charter'


        if len(school['Principal Name']) > 0:
            org['principal']        = school['Principal Name'].title()

        if len(school['Principal Phone Number']) > 0:
            org['principalPhone']  = school['Principal Phone Number']

        if len(school['Community District']) > 0:
            org['communityBoard'] = school['Community District']

        if len(school['Council District']) > 0:
            org['district'] = school['Council District']

        org['gradesTaught'] = [
            normgrade(g) for g in school['Grades'].strip().lower().split(',')
        ]

        if school['ATS System Code'] in nycod:
            opendata = nycod[school['ATS System Code']]
            location1 = opendata['Location 1'].split("\n")

            if len(location1) > 2:
                latitude, longitude = location1[-1].strip().lstrip('(').rstrip(')').split(', ')

                org['latitude'] = float(latitude)
                org['longitude'] = float(longitude)

        org['id'] = str(uuid.UUID(bytes=mmh3.hash_bytes('{}:{}'.format(
            org['type'],
            org['syncId']
        ))))

        try:
            prospectiveorgs.create(org)
        except:
            prospectiveorgs.update(org)

    except:
        logging.exception('Error:')
        continue
