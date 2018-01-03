from __future__ import absolute_import
from __future__ import unicode_literals
from .endpoints import CollectionView
# from flask import jsonify


class MetacollectionView(CollectionView):
    results_only    = True
    default_sort    = ['order']


class MetaAmmoniaMethods(MetacollectionView):
    route_base      = 'ammonia-methods'
    collection_name = 'metaammoniamethods'


class MetaAmmoniaUnits(MetacollectionView):
    route_base      = 'ammonia-units'
    collection_name = 'metaammoniaunits'


class MetaBioaccumulations(MetacollectionView):
    route_base      = 'bioaccumulations'
    collection_name = 'metabioaccumulations'


class MetaBodiesOfWater(MetacollectionView):
    route_base      = 'bodies-of-water'
    collection_name = 'metabodiesofwater'


class MetaBoroughsCounties(MetacollectionView):
    route_base      = 'boroughs-counties'
    collection_name = 'metaboroughscounties'


class MetaCclsElaScienceTechnicalSubjects(MetacollectionView):
    route_base      = 'ccls-ela-science-technical-subjects'
    collection_name = 'metacclselasciencetechnicalsubjects'


class MetaCclsMathematics(MetacollectionView):
    route_base      = 'ccls-mathematics'
    collection_name = 'metacclsmathematics'


class MetaDissolvedOxygenMethods(MetacollectionView):
    route_base      = 'dissolved-oxygen-methods'
    collection_name = 'metadissolvedoxygenmethods'


class MetaDissolvedOxygenUnits(MetacollectionView):
    route_base      = 'dissolved-oxygen-units'
    collection_name = 'metadissolvedoxygenunits'


class MetaEventTypes(MetacollectionView):
    route_base      = 'event-types'
    collection_name = 'metaeventtypes'


class MetaGarbageExtents(MetacollectionView):
    route_base      = 'garbage-extents'
    collection_name = 'metagarbageextents'


class MetaNgssCrossCuttingConcepts(MetacollectionView):
    route_base      = 'ngss-cross-cutting-concepts'
    collection_name = 'metangsscrosscuttingconcepts'


class MetaNgssDisciplinaryCoreIdeas(MetacollectionView):
    route_base      = 'ngss-disciplinary-core-ideas'
    collection_name = 'metangssdisciplinarycoreideas'


class MetaNgssScienceEngineeringPractices(MetacollectionView):
    route_base      = 'ngss-science-engineering-practices'
    collection_name = 'metangssscienceengineeringpractices'


class MetaNitrateMethods(MetacollectionView):
    route_base      = 'nitrate-methods'
    collection_name = 'metanitratemethods'


class MetaNitrateUnits(MetacollectionView):
    route_base      = 'nitrate-units'
    collection_name = 'metanitrateunits'


class MetaNycssUnits(MetacollectionView):
    route_base      = 'nycss-units'
    collection_name = 'metanycssunits'


class MetaNysssKeyIdeas(MetacollectionView):
    route_base      = 'nysss-key-ideas'
    collection_name = 'metanyssskeyideas'


class MetaNysssMajorUnderstandings(MetacollectionView):
    route_base      = 'nysss-major-understandings'
    collection_name = 'metanysssmajorunderstandings'


class MetaNysssMsts(MetacollectionView):
    route_base      = 'nysss-msts'
    collection_name = 'metanysssmsts'


class MetaOrganismCategories(MetacollectionView):
    route_base      = 'organism-categories'
    collection_name = 'metaorganismcategories'


class MetaPhMethods(MetacollectionView):
    route_base      = 'ph-methods'
    collection_name = 'metaphmethods'


class MetaPhUnits(MetacollectionView):
    route_base      = 'ph-units'
    collection_name = 'metaphunits'


class MetaSalinityMethods(MetacollectionView):
    route_base      = 'salinity-methods'
    collection_name = 'metasalinitymethods'


class MetaSalinityUnits(MetacollectionView):
    route_base      = 'salinity-units'
    collection_name = 'metasalinityunits'


class MetaShorelineTypes(MetacollectionView):
    route_base      = 'shoreline-types'
    collection_name = 'metashorelinetypes'


class MetaSubjectAreas(MetacollectionView):
    route_base      = 'subject-areas'
    collection_name = 'metasubjectareas'


class MetaTrueFalses(MetacollectionView):
    route_base      = 'true-falses'
    collection_name = 'metatruefalses'


class MetaTurbidityMethods(MetacollectionView):
    route_base      = 'turbidity-methods'
    collection_name = 'metaturbiditymethods'


class MetaTurbidityUnits(MetacollectionView):
    route_base      = 'turbidity-units'
    collection_name = 'metaturbidityunits'


class MetaWaterColors(MetacollectionView):
    route_base      = 'water-colors'
    collection_name = 'metawatercolors'


class MetaWaterFlows(MetacollectionView):
    route_base      = 'water-flows'
    collection_name = 'metawaterflows'


class MetaWaterTemperatureMethods(MetacollectionView):
    route_base      = 'water-temperature-methods'
    collection_name = 'metawatertemperaturemethods'


class MetaWaterTemperatureUnits(MetacollectionView):
    route_base      = 'water-temperature-units'
    collection_name = 'metawatertemperatureunits'


class MetaWeatherConditions(MetacollectionView):
    route_base      = 'weather-conditions'
    collection_name = 'metaweatherconditions'


class MetaWindDirections(MetacollectionView):
    route_base      = 'wind-directions'
    collection_name = 'metawinddirections'