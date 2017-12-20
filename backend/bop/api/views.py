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


class Lessonactivities(CollectionView):
    route_base      = 'lessonactivities'
    collection_name = 'lessonactivities'


class Lessonfeedbacks(CollectionView):
    route_base      = 'lessonfeedbacks'
    collection_name = 'lessonfeedbacks'


class Lessons(CollectionView):
    route_base      = 'lessons'
    collection_name = 'lessons'


class Lessontrackers(CollectionView):
    route_base      = 'lessontrackers'
    collection_name = 'lessontrackers'


class Metaammoniamethods(CollectionView):
    route_base      = 'metaammoniamethods'
    collection_name = 'metaammoniamethods'


class Metaammoniaunits(CollectionView):
    route_base      = 'metaammoniaunits'
    collection_name = 'metaammoniaunits'


class Metabioaccumulations(CollectionView):
    route_base      = 'metabioaccumulations'
    collection_name = 'metabioaccumulations'


class Metabodiesofwater(CollectionView):
    route_base      = 'metabodiesofwater'
    collection_name = 'metabodiesofwater'


class Metaboroughscounties(CollectionView):
    route_base      = 'metaboroughscounties'
    collection_name = 'metaboroughscounties'


class Metacclselasciencetechnicalsubjects(CollectionView):
    route_base      = 'metacclselasciencetechnicalsubjects'
    collection_name = 'metacclselasciencetechnicalsubjects'


class Metacclsmathematics(CollectionView):
    route_base      = 'metacclsmathematics'
    collection_name = 'metacclsmathematics'


class Metadissolvedoxygenmethods(CollectionView):
    route_base      = 'metadissolvedoxygenmethods'
    collection_name = 'metadissolvedoxygenmethods'


class Metadissolvedoxygenunits(CollectionView):
    route_base      = 'metadissolvedoxygenunits'
    collection_name = 'metadissolvedoxygenunits'


class Metaeventtypes(CollectionView):
    route_base      = 'metaeventtypes'
    collection_name = 'metaeventtypes'


class Metagarbageextents(CollectionView):
    route_base      = 'metagarbageextents'
    collection_name = 'metagarbageextents'


class Metangsscrosscuttingconcepts(CollectionView):
    route_base      = 'metangsscrosscuttingconcepts'
    collection_name = 'metangsscrosscuttingconcepts'


class Metangssdisciplinarycoreideas(CollectionView):
    route_base      = 'metangssdisciplinarycoreideas'
    collection_name = 'metangssdisciplinarycoreideas'


class Metangssscienceengineeringpractices(CollectionView):
    route_base      = 'metangssscienceengineeringpractices'
    collection_name = 'metangssscienceengineeringpractices'


class Metanitratemethods(CollectionView):
    route_base      = 'metanitratemethods'
    collection_name = 'metanitratemethods'


class Metanitrateunits(CollectionView):
    route_base      = 'metanitrateunits'
    collection_name = 'metanitrateunits'


class Metanycssunits(CollectionView):
    route_base      = 'metanycssunits'
    collection_name = 'metanycssunits'


class Metanyssskeyideas(CollectionView):
    route_base      = 'metanyssskeyideas'
    collection_name = 'metanyssskeyideas'


class Metanysssmajorunderstandings(CollectionView):
    route_base      = 'metanysssmajorunderstandings'
    collection_name = 'metanysssmajorunderstandings'


class Metanysssmsts(CollectionView):
    route_base      = 'metanysssmsts'
    collection_name = 'metanysssmsts'


class Metaorganismcategories(CollectionView):
    route_base      = 'metaorganismcategories'
    collection_name = 'metaorganismcategories'


class Metaphmethods(CollectionView):
    route_base      = 'metaphmethods'
    collection_name = 'metaphmethods'


class Metaphunits(CollectionView):
    route_base      = 'metaphunits'
    collection_name = 'metaphunits'


class Metasalinitymethods(CollectionView):
    route_base      = 'metasalinitymethods'
    collection_name = 'metasalinitymethods'


class Metasalinityunits(CollectionView):
    route_base      = 'metasalinityunits'
    collection_name = 'metasalinityunits'


class Metashorelinetypes(CollectionView):
    route_base      = 'metashorelinetypes'
    collection_name = 'metashorelinetypes'


class Metasubjectareas(CollectionView):
    route_base      = 'metasubjectareas'
    collection_name = 'metasubjectareas'


class Metatruefalses(CollectionView):
    route_base      = 'metatruefalses'
    collection_name = 'metatruefalses'


class Metaturbiditymethods(CollectionView):
    route_base      = 'metaturbiditymethods'
    collection_name = 'metaturbiditymethods'


class Metaturbidityunits(CollectionView):
    route_base      = 'metaturbidityunits'
    collection_name = 'metaturbidityunits'


class Metawatercolors(CollectionView):
    route_base      = 'metawatercolors'
    collection_name = 'metawatercolors'


class Metawaterflows(CollectionView):
    route_base      = 'metawaterflows'
    collection_name = 'metawaterflows'


class Metawatertemperaturemethods(CollectionView):
    route_base      = 'metawatertemperaturemethods'
    collection_name = 'metawatertemperaturemethods'


class Metawatertemperatureunits(CollectionView):
    route_base      = 'metawatertemperatureunits'
    collection_name = 'metawatertemperatureunits'


class Metaweatherconditions(CollectionView):
    route_base      = 'metaweatherconditions'
    collection_name = 'metaweatherconditions'


class Metawinddirections(CollectionView):
    route_base      = 'metawinddirections'
    collection_name = 'metawinddirections'


class Mobileorganisms(CollectionView):
    route_base      = 'mobileorganisms'
    collection_name = 'mobileorganisms'


class Protocolmobiletraps(CollectionView):
    route_base      = 'protocolmobiletraps'
    collection_name = 'protocolmobiletraps'


class Protocoloystermeasurements(CollectionView):
    route_base      = 'protocoloystermeasurements'
    collection_name = 'protocoloystermeasurements'


class Protocolsettlementtiles(CollectionView):
    route_base      = 'protocolsettlementtiles'
    collection_name = 'protocolsettlementtiles'


class Protocolsiteconditions(CollectionView):
    route_base      = 'protocolsiteconditions'
    collection_name = 'protocolsiteconditions'


class Protocolwaterqualities(CollectionView):
    route_base      = 'protocolwaterqualities'
    collection_name = 'protocolwaterqualities'


class Researchactivities(CollectionView):
    route_base      = 'researchactivities'
    collection_name = 'researchactivities'


class Researches(CollectionView):
    route_base      = 'researches'
    collection_name = 'researches'


class Researchfeedbacks(CollectionView):
    route_base      = 'researchfeedbacks'
    collection_name = 'researchfeedbacks'


class Restorationstations(CollectionView):
    route_base      = 'restorationstations'
    collection_name = 'restorationstations'


class Savedlessons(CollectionView):
    route_base      = 'savedlessons'
    collection_name = 'savedlessons'


class Savedresearches(CollectionView):
    route_base      = 'savedresearches'
    collection_name = 'savedresearches'


class Schoolorgs(CollectionView):
    route_base      = 'schoolorgs'
    collection_name = 'schoolorgs'


class Sessileorganisms(CollectionView):
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


class Teamrequests(CollectionView):
    route_base      = 'teamrequests'
    collection_name = 'teamrequests'


class Teams(CollectionView):
    route_base      = 'teams'
    collection_name = 'teams'


class Unitactivities(CollectionView):
    route_base      = 'unitactivities'
    collection_name = 'unitactivities'


class Units(CollectionView):
    route_base      = 'units'
    collection_name = 'units'

    def prepare_results(self, results):
        return jsonify(list(results))


class Useractivities(CollectionView):
    route_base      = 'useractivities'
    collection_name = 'useractivities'


class Users(CollectionView):
    route_base      = 'users'
    collection_name = 'users'
