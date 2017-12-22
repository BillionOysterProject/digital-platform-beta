from requests.cookies import cookiejar_from_dict
from simplejson.scanner import JSONDecodeError
import json
import os
import requests

endpoints = [
    '/api/ammonia-units',
    '/api/articles',
    '/api/bioaccumulations',
    '/api/bodies-of-water',
    '/api/boroughs-counties',
    '/api/ccls-ela-science-technical-subjects',
    '/api/ccls-mathematics',
    '/api/dissolved-oxygen-methods',
    '/api/dissolved-oxygen-units',
    '/api/email/bug-report',
    '/api/email/general-feedback',
    '/api/email/help',
    '/api/email/share',
    '/api/email/unit-feedback',
    '/api/event-types',
    '/api/events',
    '/api/events/download-file',
    '/api/expedition-activities',
    '/api/expeditions',
    '/api/expeditions/compare',
    '/api/expeditions/export-compare',
    '/api/expeditions/restoration-station',
    '/api/garbage-extents',
    '/api/glossary',
    '/api/lessons',
    '/api/lessons/download-file',
    '/api/lessons/favorites',
    '/api/lessons/tracked-list',
    '/api/metrics/activeUsers',
    '/api/metrics/basic',
    '/api/metrics/curriculum',
    '/api/metrics/curriculum/lessons/monthlyTotals',
    '/api/metrics/curriculum/units/monthlyTotals',
    '/api/metrics/download/events',
    '/api/metrics/download/expeditions',
    '/api/metrics/download/lessons',
    '/api/metrics/download/misc',
    '/api/metrics/download/organizations',
    '/api/metrics/download/team-leads',
    '/api/metrics/download/team-members',
    '/api/metrics/events',
    '/api/metrics/events/monthlyTotals',
    '/api/metrics/events/statistics',
    '/api/metrics/expeditions/monthlyTotals',
    '/api/metrics/people',
    '/api/metrics/people-with-admin',
    '/api/metrics/stations',
    '/api/metrics/stations/monthlyTotals',
    '/api/mobile-organisms',
    '/api/ngss-cross-cutting-concepts',
    '/api/ngss-disciplinary-core-ideas',
    '/api/ngss-science-engineering-practices',
    '/api/nitrate-methods',
    '/api/nitrate-units',
    '/api/nycsss-units',
    '/api/nysss-key-ideas',
    '/api/nysss-major-understandings',
    '/api/nysss-mst',
    '/api/organism-categories',
    '/api/ph-methods',
    '/api/ph-units',
    '/api/property-owners',
    '/api/remote-files/delete-file',
    '/api/remote-files/upload-wysiwyg-images',
    '/api/research',
    '/api/research/favorites',
    '/api/restoration-stations',
    '/api/restoration-stations/property-owners',
    '/api/restoration-stations/site-coordinators',
    '/api/salinity-methods',
    '/api/salinity-units',
    '/api/school-orgs',
    '/api/sessile-organisms',
    '/api/shoreline-types',
    '/api/sites',
    '/api/subject-areas',
    '/api/team-requests',
    '/api/teams',
    '/api/teams/members',
    '/api/tide-tables',
    '/api/true-falses',
    '/api/turbidity-methods',
    '/api/turbidity-units',
    '/api/units',
    '/api/users',
    '/api/users/accounts',
    '/api/users/accounts',
    '/api/users/leaders',
    '/api/users/leaders/csv',
    '/api/users/leaders/validate/csv',
    '/api/users/password',
    '/api/users/password',
    '/api/users/picture',
    '/api/users/picture',
    '/api/users/teamleads',
    '/api/users/teamleads',
    '/api/users/username',
    '/api/water-colors',
    '/api/water-flows',
    '/api/water-temperature-methods',
    '/api/water-temperature-units',
    '/api/weather-conditions',
    '/api/wind-directions',
]

session = requests.Session()
session.cookies = cookiejar_from_dict({
    'sessionId': os.environ.get('SESSION'),
})

for endpoint in endpoints:
    try:
        old = session.get('https://platform.bop.nyc{}'.format(endpoint))

        if old.status_code >= 400:
            print('{}\tHTTP {} (old)'.format(endpoint, old.status_code))
            continue

        old = old.json()
    except JSONDecodeError:
        print('{}\tnot JSON'.format(endpoint))
        continue

    try:
        new = session.get('http://localhost:5000{}'.format(endpoint))

        if new.status_code >= 400:
            print('{}\tHTTP {} (new)'.format(endpoint, new.status_code))
            continue

        new = new.json()
    except JSONDecodeError:
        continue

    if isinstance(old, list):
        if isinstance(new, dict):
            if new.get('totalCount'):
                print('{}\tnew needs results_only'.format(endpoint))
            else:
                print('{}\tnew is a dict of some kind: {}'.format(
                    endpoint,
                    json.dumps(new, indent=4)
                ))
        elif not isinstance(new, list):
                print('{}\told returned list, new returned {}'.format(
                    endpoint,
                    new.__class__
                ))

                print('new:')
                print(json.dumps(new, indent=4))
        else:
            if not len(old):
                print('{}\tcannot compare; old list is empty'.format(endpoint))
                continue
            elif not len(new):
                print('{}\tcannot compare; new list is empty'.format(endpoint))
                continue
            else:
                o1 = old[0]
                n1 = new[0]

                if isinstance(o1, dict):
                    if not isinstance(n1, dict):
                        print('{}\told[0] is dict, new[0] is {}'.format(
                            endpoint,
                            new.__class__
                        ))
                        continue

                    else:
                        try:
                            for k, v in o1.items():
                                if k not in n1:
                                    print('{}\told[0] has key {}, missing in new[0]'.format(
                                        endpoint,
                                        k
                                    ))
                                    raise StopIteration
                        except StopIteration:
                            continue

                        try:
                            for k, v in n1.items():
                                if k not in o1:
                                    print('{}\told[0] missing key {} from new[0]'.format(
                                        endpoint,
                                        k
                                    ))
                                    raise StopIteration
                        except StopIteration:
                            continue
