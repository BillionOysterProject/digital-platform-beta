from __future__ import absolute_import
from __future__ import unicode_literals
from .endpoints import CollectionView
from flask import jsonify


class Calendarevents(CollectionView):
    route_base      = 'calendarevents'
    collection_name = 'calendarevents'


class Circles(CollectionView):
    route_base      = 'circles'
    collection_name = 'circles'


class ExpeditionActivities(CollectionView):
    route_base      = 'expeditionactivities'
    collection_name = 'expeditionactivities'


class Expeditions(CollectionView):
    route_base      = 'expeditions'
    collection_name = 'expeditions'


class Glossaries(CollectionView):
    route_base      = 'glossaries'
    collection_name = 'glossaries'


class LessonActivities(CollectionView):
    route_base      = 'lessonactivities'
    collection_name = 'lessonactivities'


class LessonFeedbacks(CollectionView):
    route_base      = 'lessonfeedbacks'
    collection_name = 'lessonfeedbacks'


class Lessons(CollectionView):
    route_base      = 'lessons'
    collection_name = 'lessons'


class LessonTrackers(CollectionView):
    route_base      = 'lessontrackers'
    collection_name = 'lessontrackers'


class MobileOrganisms(CollectionView):
    route_base      = 'mobileorganisms'
    collection_name = 'mobileorganisms'


class ProtocolMobileTraps(CollectionView):
    route_base      = 'protocolmobiletraps'
    collection_name = 'protocolmobiletraps'


class ProtocolOysterMeasurements(CollectionView):
    route_base      = 'protocoloystermeasurements'
    collection_name = 'protocoloystermeasurements'


class ProtocolSettlementTiles(CollectionView):
    route_base      = 'protocolsettlementtiles'
    collection_name = 'protocolsettlementtiles'


class ProtocolSiteConditions(CollectionView):
    route_base      = 'protocolsiteconditions'
    collection_name = 'protocolsiteconditions'


class ProtocolWaterQualities(CollectionView):
    route_base      = 'protocolwaterqualities'
    collection_name = 'protocolwaterqualities'


class ResearchActivities(CollectionView):
    route_base      = 'researchactivities'
    collection_name = 'researchactivities'


class Researches(CollectionView):
    route_base      = 'researches'
    collection_name = 'researches'


class ResearchFeedbacks(CollectionView):
    route_base      = 'researchfeedbacks'
    collection_name = 'researchfeedbacks'


class RestorationStations(CollectionView):
    route_base      = 'restorationstations'
    collection_name = 'restorationstations'


class SavedLessons(CollectionView):
    route_base      = 'savedlessons'
    collection_name = 'savedlessons'


class SavedResearches(CollectionView):
    route_base      = 'savedresearches'
    collection_name = 'savedresearches'


class SchoolOrgs(CollectionView):
    route_base      = 'schoolorgs'
    collection_name = 'schoolorgs'


class SessileOrganisms(CollectionView):
    route_base      = 'sessileorganisms'
    collection_name = 'sessileorganisms'


class Sessions(CollectionView):
    route_base      = 'sessions'
    collection_name = 'sessions'


class Sites(CollectionView):
    route_base      = 'sites'
    collection_name = 'sites'


class SystemIndexes(CollectionView):
    route_base      = 'system.indexes'
    collection_name = 'system.indexes'


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


class UnitActivities(CollectionView):
    route_base      = 'unitactivities'
    collection_name = 'unitactivities'


class Units(CollectionView):
    route_base      = 'units'
    collection_name = 'units'
    results_only    = True
    expand_fields   = {
        'user': (
            'users', ['_id', 'displayName'],
        ),
        'parentUnits': (
            'units', ['_id', 'status', 'icon', 'color', 'title'],
        )
    }


class UserActivities(CollectionView):
    route_base      = 'useractivities'
    collection_name = 'useractivities'


class Users(CollectionView):
    route_base      = 'users'
    collection_name = 'users'
