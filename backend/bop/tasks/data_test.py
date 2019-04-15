from __future__ import absolute_import
from unittest import TestCase
from collections import OrderedDict
from .data import populate_expedition_record, EXPEDITION_DATA_EXPORT_FIELDS


class TaskDataPopulateTest(TestCase):
    def test_populate_expedition_record(self):
        record = OrderedDict()

        x = {
            '_id':                 'abc123',
            'monitoringStartDate': '2018-09-28T19:00:00Z',
            'name':                'Test One',
            'notes':               'notes',
            'status':              'published',
            'updated':             '2018-10-19T19:38:29.555Z',
            'published':           '2018-11-02T19:07:18.917Z',
            'protocols': {
                'siteCondition': {
                    'meteorologicalConditions': {
                        'airTemperatureC':   17,
                        'humidityPer':       79,
                        'weatherConditions': 'cloudy',
                        'windDirection':     'northeast',
                        'windSpeedMPH':      3
                    },
                    'recentRainfall': {
                        'rainedIn24Hours': True,
                        'rainedIn72Hours': True,
                        'rainedIn7Days':   True
                    },
                    'waterConditions': {
                        'garbage': {
                            'garbagePresent': True,
                            'glass':          'none',
                            'hardPlastic':    'sporadic',
                            'metal':          'none',
                            'organic':        'sporadic',
                            'paper':          'none',
                            'softPlastic':    'sporadic',
                        },
                        'markedCombinedSewerOverflowPipes': {
                            'markedCSOPresent': False,
                        },
                        'oilSheen':   False,
                        'waterColor': 'darkGreen',
                        'unmarkedOutfallPipes': {
                            'approximateDiameterCM': 50,
                            'howMuchFlowThrough':    'trickle',
                            'unmarkedPipePresent':   True
                        },
                    },
                },
                'waterQuality': {
                    'status':         'published',
                    'submitted':      '2018-10-22T22:53:30.774Z',
                    'collectionTime': '2018-10-19T19:38:00Z',
                    'samples': [{
                        'ammonia': {
                            'results': [],
                        },
                        'dissolvedOxygen': {
                            'results': [],
                        },
                        'locationOfWaterSample': {
                            'latitude':  40.734716,
                            'longitude': -73.974308,
                        },
                        'nitrates': {
                            'results': [],
                        },
                        'others': [{
                            'results': [],
                        }],
                        'pH': {
                            'results': [],
                        },
                        'salinity': {
                            'results': [],
                        },
                        'turbidity': {
                            'results': [],
                        },
                        'waterTemperature': {
                            'average': 21,
                            'method':  'analogThermometer',
                            'results': [
                                21,
                                21,
                                None,
                            ],
                            'units':   'c',
                        }
                    }, {
                        'ammonia': {
                            'average': 2,
                            'method': 'testStrips',
                            'results': [1, 2, 3],
                            'units': 'ppm'
                        },
                        'dissolvedOxygen': {
                            'average': 2,
                            'method': 'colormetricvAmpules',
                            'results': [1, 2, 3],
                            'units': 'mgl'
                        },
                        'locationOfWaterSample': {
                            'latitude': 40.69144210646147,
                            'longitude': -74.01216745376587
                        },
                        'nitrates': {
                            'average': 2,
                            'method': 'testStrips',
                            'results': [1, 2, 3],
                            'units': 'ppm'
                        },
                        'others': [{
                            'average': 2,
                            'label': 'entero',
                            'method': 'idex tray',
                            'results': [1, 2, 3],
                            'units': 'mpn'
                        }],
                        'pH': {
                            'average': 2,
                            'method': 'sensorRO',
                            'results': [1, 2, 3],
                            'units': 'pHlogscale'
                        },
                        'salinity': {
                            'average': 2,
                            'method': 'hydrometer',
                            'results': [1, 2, 3],
                            'units': 'ppt'
                        },
                        'turbidity': {
                            'average': 2,
                            'method': 'turbidityTube',
                            'results': [1, 2, 3],
                            'units': 'cm'
                        },
                        'waterTemperature': {
                            'average': 50.67,
                            'method': 'digitalThermometer',
                            'results': [50, 50, 52],
                            'units': 'f'
                        }
                    }],
                },
                'mobileTrap': {
                    'mobileOrganisms': [
                        {
                            'count': 1,
                            'notesQuestions': 'kinda gross',
                            'organism': {
                                'category': 'crustaceans',
                                'commonName': 'Black-fingered mud crab',
                                'latinName': 'Panopeus herbstii'
                            }
                        },
                        {
                            'count': 3,
                            'organism': {
                                'category': 'fish',
                                'commonName': 'Blackfish, Tautog',
                                'latinName': 'Tautoga onitis'
                            }
                        },
                        {
                            'count': 5,
                            'organism': {
                                'category': 'crustaceans',
                                'commonName': 'Blue crab',
                                'latinName': 'Callinectes sapidus'
                            }
                        },
                        {
                            'count': 3,
                            'organism': {
                                'category': 'worms',
                                'commonName': 'Clam worm',
                                'latinName': 'Nereis spp.'
                            }
                        },
                        {
                            'count': 2,
                            'organism': {
                                'category': 'crustaceans',
                                'commonName': 'Corophid amphipod',
                                'latinName': 'Family Corophidae (commonly Corophium volutator)'
                            }
                        },
                        {
                            'count': 4,
                            'organism': {
                                'category': 'crustaceans',
                                'commonName': 'Gammarid amphipod, scud',
                                'latinName': 'Gammarus spp.'
                            }
                        },
                        {
                            'count': 6,
                            'organism': {
                                'category': 'crustaceans',
                                'commonName': 'Green crab',
                                'latinName': 'Carcinus maenas'
                            }
                        },
                        {
                            'count': 4,
                            'organism': {
                                'category': 'crustaceans',
                                'commonName': 'Idotea isopod',
                                'latinName': 'Idotea spp.'
                            }
                        },
                        {
                            'count': 2,
                            'organism': {
                                'category': 'crustaceans',
                                'commonName': 'Japanese shore crab, Asian shore crab',
                                'latinName': 'Hemigrapsus sanguineus'
                            }
                        },
                        {
                            'count': 1,
                            'organism': {
                                'category': 'fish',
                                'commonName': 'Northern pipefish',
                                'latinName': 'Syngnathus fuscus'
                            }
                        },
                        {
                            'count': 1,
                            'organism': {
                                'category': 'fish',
                                'commonName': 'Northern sea robin',
                                'latinName': 'Prionotus carolinus'
                            }
                        },
                        {
                            'count': 1,
                            'organism': {
                                'category': 'worms',
                                'commonName': 'Oyster flatworm',
                                'latinName': 'Stylochus ellipticus'
                            }
                        },
                        {
                            'count': 1,
                            'organism': {
                                'category': 'fish',
                                'commonName': 'Oyster toadfish',
                                'latinName': 'Opsanus tau'
                            }
                        },
                        {
                            'count': 1,
                            'organism': {
                                'category': 'crustaceans',
                                'commonName': 'Sea pill bug',
                                'latinName': 'Order Isopoda, Family Sphaeromatidae'
                            }
                        },
                        {
                            'count': 1,
                            'organism': {
                                'category': 'crustaceans',
                                'commonName': 'Shore shrimp, Grass shrimp',
                                'latinName': 'Palaemonetes spp.'
                            }
                        },
                        {
                            'count': 1,
                            'organism': {
                                'category': 'crustaceans',
                                'commonName': 'Tube-building amphipod',
                                'latinName': 'Jassa marmorata'
                            }
                        },
                        {
                            'count': 1,
                            'organism': {
                                'category': 'crustaceans',
                                'commonName': 'White-fingered mud crab',
                                'latinName': 'Rhithropanopeus harrisii'
                            }
                        }
                    ],
                    'notes': 'test',
                },
                'settlementTiles': {
                    'notes': 'test',
                    'settlementTiles': [{
                        'description': 'kind of covered',
                        'grid1': {
                            'organism': {
                                'commonName': 'Blue mussel',
                                'latinName': 'Mytilus edulis'
                            },
                        },
                        'grid10': {
                            'organism': {
                                'commonName': 'None/Sediment',
                                'latinName': 'N/A'
                            },
                        },
                        'grid11': {
                            'organism': {
                                'commonName': 'None/Sediment',
                                'latinName': 'N/A'
                            },
                        },
                        'grid12': {
                            'organism': {
                                'commonName': 'None/Sediment',
                                'latinName': 'N/A'
                            },
                        },
                        'grid13': {
                            'organism': {
                                'commonName': 'None/Sediment',
                                'latinName': 'N/A'
                            },
                        },
                        'grid14': {
                            'organism': {
                                'commonName': 'None/Sediment',
                                'latinName': 'N/A'
                            },
                        },
                        'grid15': {
                            'organism': {
                                'commonName': 'None/Sediment',
                                'latinName': 'N/A'
                            },
                        },
                        'grid16': {
                            'notes': {
                                'commonName': 'None/Sediment',
                                'latinName': 'N/A'
                            }
                        },
                        'grid17': {
                            'organism': {
                                'commonName': 'None/Sediment',
                                'latinName': 'N/A'
                            },
                        },
                        'grid18': {
                            'notes': {
                                'commonName': 'None/Sediment',
                                'latinName': 'N/A'
                            }
                        },
                        'grid19': {
                            'organism': {
                                'commonName': 'None/Sediment',
                                'latinName': 'N/A'
                            }
                        },
                        'grid2': {
                            'organism': {
                                'commonName': 'None/Sediment',
                                'latinName': 'N/A'
                            },
                        },
                        'grid20': {
                            'organism': {
                                'commonName': 'None/Sediment',
                                'latinName': 'N/A'
                            },
                        },
                        'grid21': {
                            'organism': {
                                'commonName': 'None/Sediment',
                                'latinName': 'N/A'
                            },
                        },
                        'grid22': {
                            'notes': {
                                'commonName': 'None/Sediment',
                                'latinName': 'N/A'
                            }
                        },
                        'grid23': {
                            'notes': {
                                'commonName': 'None/Sediment',
                                'latinName': 'N/A'
                            }
                        },
                        'grid24': {
                            'organism': {
                                'commonName': 'None/Sediment',
                                'latinName': 'N/A'
                            },
                        },
                        'grid25': {
                            'organism': {
                                'commonName': 'Boring sponges',
                                'latinName': 'Cliona spp.'
                            },
                        },
                        'grid3': {
                            'organism': {
                                'commonName': 'None/Sediment',
                                'latinName': 'N/A'
                            },
                        },
                        'grid4': {
                            'organism': {
                                'commonName': 'None/Sediment',
                                'latinName': 'N/A'
                            },
                        },
                        'grid5': {
                            'organism': {
                                'commonName': 'None/Sediment',
                                'latinName': 'N/A'
                            },
                        },
                        'grid6': {
                            'organism': {
                                'commonName': 'None/Sediment',
                                'latinName': 'N/A'
                            },
                        },
                        'grid7': {
                            'organism': {
                                'commonName': 'None/Sediment',
                                'latinName': 'N/A'
                            }
                        },
                        'grid8': {
                            'organism': {
                                'commonName': 'None/Sediment',
                                'latinName': 'N/A'
                            },
                        },
                        'grid9': {
                            'organism': {
                                'commonName': 'None/Sediment',
                                'latinName': 'N/A'
                            },
                        },
                    }, {
                        'grid1': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid10': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid11': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid12': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid13': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid14': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid15': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            },
                            'organism': None
                        },
                        'grid16': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            },
                            'organism': None
                        },
                        'grid17': {
                            'notes': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            },
                            'organism': None
                        },
                        'grid18': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid19': {
                            'notes': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            },
                            'organism': None
                        },
                        'grid2': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid20': {
                        },
                        'grid21': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid22': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid23': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid24': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            },
                            'organism': None
                        },
                        'grid25': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid3': {
                            'notes': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            },
                            'organism': None
                        },
                        'grid4': {
                            'notes': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            },
                            'organism': None
                        },
                        'grid5': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid6': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid7': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            },
                            'organism': None
                        },
                        'grid8': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            },
                            'organism': None
                        },
                        'grid9': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        }
                    },
                    {
                        'grid1': {
                            'notes': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            },
                            'organism': None
                        },
                        'grid10': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid11': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid12': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid13': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid14': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid15': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid16': {
                            'notes': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            },
                            'organism': None
                        },
                        'grid17': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid18': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid19': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid2': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid20': {
                        },
                        'grid21': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid22': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid23': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            },
                            'organism': None
                        },
                        'grid24': {
                            'notes': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            },
                            'organism': None
                        },
                        'grid25': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            },
                            'organism': None
                        },
                        'grid3': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid4': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid5': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid6': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid7': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid8': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid9': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        }
                    }, {
                        'grid1': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid10': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid11': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid12': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid13': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid14': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid15': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid16': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid17': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid18': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid19': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            },
                        },
                        'grid2': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid20': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid21': {
                            'notes': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            },
                            'organism': None
                        },
                        'grid22': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid23': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid24': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid25': {
                            'notes': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            },
                            'organism': None
                        },
                        'grid3': {
                            'notes': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            },
                            'organism': None
                        },
                        'grid4': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid5': {
                            'notes': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            },
                            'organism': None
                        },
                        'grid6': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            },
                            'organism': None
                        },
                        'grid7': {
                            'notes': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            },
                            'organism': None
                        },
                        'grid8': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        },
                        'grid9': {
                            'organism': {
                                '_collection': 'sessileorganisms',
                                '_id': None,
                                '_missing': True
                            }
                        }
                    }],
                },
            },
            'station': {
                'name':          'Test Station',
                'structureType': 'research-station',
                'site': {
                    'bodyOfWater':   'East River',
                    'boroughCounty': 'Manhattan',
                    'latitude':      40.734716,
                    'longitude':     -73.974308,
                    'name':          'Test Site',
                    'state':         'NY',
                },
            },
            'team': {
                'name': 'Test Team',
                'schoolOrg': {
                    'name':  'Test Organization',
                    'city':  'Manhattan',
                    'state': 'NY',
                },
            },
        }

        for flt in EXPEDITION_DATA_EXPORT_FIELDS:
            populate_expedition_record(record, x, flt)

        self.assertEqual(record['Expedition ID'],                      'abc123')
        self.assertEqual(record['Date-Time'],                          '2018-09-28T19:00:00Z')
        self.assertEqual(record['Organism: Blackfish, Tautog'],        3)
        self.assertEqual(record['Organism: Blue crab'],                5)
        self.assertEqual(record['Organism: Green crab'],               6)
        self.assertEqual(record['Organism: Green crab'],               6)
        self.assertEqual(record['# of Grid Pts: Blue mussel'],         1)
        self.assertEqual(record['# of Grid Pts: None/Sediment'],       19)
        self.assertEqual(record['# of Grid Pts: Boring sponges'],      1)
        self.assertEqual(record['Tile 1, Grid Pt. 1'],                 'Blue mussel')
        self.assertEqual(record['Sample 1: Water Temperature Method'], 'analogThermometer')
        self.assertEqual(record['Sample 2: Nitrates Method'],          'testStrips')