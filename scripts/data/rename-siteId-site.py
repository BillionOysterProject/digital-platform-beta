# flake8: noqa
from __future__ import unicode_literals
import pivot
import sys
import re
import csv
import time

client = pivot.Client()

stations = client.collection('restorationstations')

for station in stations.all(limit=False, noexpand=True):
    if station.site != station.siteId:
        station.site = station.siteId
        print('Station {} status={} site={}->{}'.format(station.id, station.status, station.siteId, station.site))
        stations.update(station)