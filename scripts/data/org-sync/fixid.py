# flake8: noqa
import pivot
import csv
import sys

client = pivot.Client()
schoolorgs = client.collection('schoolorgs')

for org in schoolorgs.query('all', limit=10000):
    org['creator']          = org.get('creator', '5707ec9277d0beb8cb1c8e19')

    org['creator'] = org['creator'].replace('ObjectIdHex("', '')
    org['creator'] = org['creator'].replace('")', '')

    org['pending'] = False

    schoolorgs.update(org)
