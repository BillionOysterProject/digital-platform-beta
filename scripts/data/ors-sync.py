# flake8: noqa
from __future__ import unicode_literals
import pivot
import sys
import re
import csv
import time

client = pivot.Client()

stations = client.collection('restorationstations')
sites = client.collection('sites')


with open('scripts/data/ors.tsv', 'rU') as file:
    reader = csv.DictReader(file, dialect='excel-tab')

    i = 0

    for row in reader:
        results = sites.query('name/like:{}/bodyOfWater/like:{}'.format(
            re.sub(r'\s+', ' ', row['name']).strip(),
            re.sub(r'\s+', ' ', row['bodyOfWater']).strip(),
        ))

        site = None

        if len(results.records):
            site = results.records[0]
        elif row['ors_id'] == '58001f2fc69cc4820e2bef68':
            site = sites.get('5aa8337061d6e00b838b30a1')

        if site:
            status = row['status'].lower()

            if status == 'destroyed':
                status = 'damaged-destroyed'

            ors = stations.get(row['ors_id'])

            ors['site']        = site.id
            # ors['status']        = status
            ors['latitude']      = float(site.latitude)
            ors['longitude']     = float(site.longitude)
            ors['boroughCounty'] = site.boroughCounty

            if len(site.name) and len(site.bodyOfWater):
                ors['bodyOfWater']   = '{}, {}'.format(site.name, site.bodyOfWater)

            print(ors.id)
            stations.update(ors)

        else:
            print('No site: "{}" "{}"'.format(row['name'], row['bodyOfWater']))
