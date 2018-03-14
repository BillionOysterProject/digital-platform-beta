# flake8: noqa
from __future__ import unicode_literals
import pivot
import csv
import sys
import re

client = pivot.Client()

schoolOrgs      = client.collection('schoolorgs')
prospectiveOrgs = client.collection('prospectiveorgs')

SKIP_FIELDS = (
    'created',
    'creator',
    'description',
    'id',
    'name',
    'organizationType',
    'pending',
    'schoolType',
)

# for each school-org in the database...
for school in schoolOrgs.query('all', limit=False):
    if school.syncId:
        has_changed = False

        try:
            aProspectiveOrg = prospectiveOrgs.query('syncId/{}'.format(school.syncId), limit=1).records[0]
        except IndexError:
            print('Unchanged: {}'.format(school.id))
            continue

        for k, v in school.items():
            if k in SKIP_FIELDS:
                continue

            if k in aProspectiveOrg:
                if school[k] != aProspectiveOrg[k]:
                    has_changed = True
                    school[k] = aProspectiveOrg[k]
                    print('  [U] {}={}'.format(k, school[k]))

        for k in [
            'latitude',
            'longitude',
        ]:
            v = aProspectiveOrg.get(k)

            if v and school.get(k) != v:
                school[k] = v
                has_changed = True
                print('  [U] {}={}'.format(k, school[k]))

        if has_changed:
            print('   Synced: {} ({})'.format(school.id, school.name))
            schoolOrgs.update(school)
        else:
            print('Unchanged: {}'.format(school.id))


