# flake8: noqa
from __future__ import unicode_literals
import pivot
import sys
import re

client = pivot.Client()
stations = client.collection('restorationstations')
expeditions = client.collection('expeditions')
users = client.collection('users')


for station in stations.all(limit=False, sort=['name']):
    outputs = [
        station.id,
        station.name,
        station.status,
    ]
    date = None

    try:
        lastExpedition = expeditions.query(
            'station/{}/status/published'.format(station.id),
            sort=['-published'],
            limit=1
        ).records[0]

        date = lastExpedition['fields'].get('published')
    except IndexError:
        pass

    if date:
        outputs.append(date)
    else:
        outputs.append('')

    try:
        stationOwner = users.get(station.teamLead)
    except pivot.exceptions.RecordNotFound:
        stationOwner = None

    if stationOwner:
        outputs.append(stationOwner.displayName)
        outputs.append(stationOwner.email)
    else:
        outputs.append('')
        outputs.append('')

    print('\t'.join(outputs))
