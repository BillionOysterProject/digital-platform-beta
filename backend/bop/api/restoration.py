from __future__ import absolute_import
from __future__ import unicode_literals
from .endpoints import CollectionView
from flask import jsonify, g, request
from flask_classy import route
from collections import OrderedDict
import dpath.util


class ExpeditionActivities(CollectionView):
    route_base      = 'expedition-activities'
    collection_name = 'expeditionactivities'
    results_only    = True


class Expeditions(CollectionView):
    route_base      = 'expeditions'
    collection_name = 'expeditions'

    expand_fields   = {
        'teamLead': (
            'users', ['_id', 'displayName', 'username', 'profileImageURL'],
        ),
        'team': (
            'teams', ['_id', 'name', 'schoolOrg'],
        ),
        'station': (
            'restorationstations', ['_id', 'name'],
        ),
        'teamLists.mobileTrap': (
            'users', ['_id', 'displyaName', 'username', 'profileImageURL'],
        ),
        'teamLists.oysterMeasurement': (
            'users', ['_id', 'displayName', 'username', 'profileImageURL'],
        ),
        'teamLists.settlementTiles': (
            'users', ['_id', 'displayName', 'username', 'profileImageURL'],
        ),
        'teamLists.siteCondition': (
            'users', ['_id', 'displayName', 'username', 'profileImageURL'],
        ),
        'teamLists.waterQuality': (
            'users', ['_id', 'displayName', 'username', 'profileImageURL'],
        ),
        'protocols.mobileTrap': (
            'protocolmobiletraps', ['_id', 'status'],
        ),
        'protocols.oysterMeasurement': (
            'protocoloystermeasurements', ['_id', 'status'],
        ),
        'protocols.settlementTiles': (
            'protocolsettlementtiles', ['_id', 'status'],
        ),
        'protocols.siteCondition': (
            'protocolsiteconditions', ['_id', 'status'],
        ),
        'protocols.waterQuality': (
            'protocolwaterqualities', ['_id', 'status'],
        ),
    }


class ProtocolSiteConditions(CollectionView):
    route_base      = 'protocol-site-conditions'
    collection_name = 'protocolsiteconditions'


class ProtocolOysterMeasurements(CollectionView):
    route_base      = 'protocol-oyster-measurements'
    collection_name = 'protocoloystermeasurements'


class ProtocolMobileTraps(CollectionView):
    route_base      = 'protocol-mobile-traps'
    collection_name = 'protocolmobiletraps'


class ProtocolSettlementTiles(CollectionView):
    route_base      = 'protocol-settlement-tiles'
    collection_name = 'protocolsettlementtiles'


class ProtocolWaterQualities(CollectionView):
    route_base      = 'protocol-water-qualities'
    collection_name = 'protocolwaterqualities'


class RestorationStations(CollectionView):
    route_base      = 'restoration-stations'
    collection_name = 'restorationstations'
    results_only    = True


class Sites(CollectionView):
    route_base      = 'sites'
    collection_name = 'sites'
    results_only    = True


class MobileOrganisms(CollectionView):
    route_base      = 'mobile-organisms'
    collection_name = 'mobileorganisms'
    results_only    = True


class SessileOrganisms(CollectionView):
    route_base      = 'sessile-organisms'
    collection_name = 'sessileorganisms'
    results_only    = True
