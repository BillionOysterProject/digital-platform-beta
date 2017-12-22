from __future__ import absolute_import
from __future__ import unicode_literals
from .endpoints import CollectionView


class TeamRequests(CollectionView):
    route_base      = 'teamrequests'
    collection_name = 'teamrequests'


class Teams(CollectionView):
    route_base      = 'teams'
    collection_name = 'teams'
    results_only    = True

    expand_fields   = {
        'schoolOrg': (
            'schoolorgs', ['_id', 'name'],
        ),
        'teamLeads': (
            'users', [],
        )
    }


class UserActivities(CollectionView):
    route_base      = 'useractivities'
    collection_name = 'useractivities'


class Users(CollectionView):
    route_base      = 'users'
    collection_name = 'users'


class Sessions(CollectionView):
    route_base      = 'sessions'
    collection_name = 'sessions'


class SchoolOrgs(CollectionView):
    route_base      = 'schoolorgs'
    collection_name = 'schoolorgs'
