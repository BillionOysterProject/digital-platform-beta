# flake8: noqa
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

        aProspectiveOrg = prospectiveOrgs.query('syncId/{}'.format(school.syncId), limit=1)

        for k, v in school.items():
            if k in SKIP_FIELDS:
                continue

            if k in aProspectiveOrg:
                if school[k] != aProspectiveOrg[k]:
                    has_changed = True
                    school[k] = aProspectiveOrg[k]

        if has_changed:
            print('   Synced: {} ({})'.format(school.id, school.name))
            schoolOrgs.update(school)
        else:
            print('Unchanged: {}'.format(school.id))

