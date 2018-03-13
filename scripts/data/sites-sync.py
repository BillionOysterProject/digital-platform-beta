# flake8: noqa
from __future__ import unicode_literals
import pivot
import sys
import re
import csv
import time

client = pivot.Client()

try:
    client.delete_collection('sites')
except:
    pass

try:
    client.create_collection('sites')
except:
    pass

time.sleep(20)

sites = client.collection('sites')


with open('scripts/data/sites.tsv', 'rU') as file:
    reader = csv.DictReader(file, dialect='excel-tab')

    for row in reader:
        sites.create(row)

print('total={}'.format(sites.count()))
