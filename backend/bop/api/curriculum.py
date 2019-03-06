from __future__ import absolute_import
from __future__ import unicode_literals
from .endpoints import CollectionView
from .meta import MetacollectionView


class UnitActivities(CollectionView):
    route_base      = 'unit-activities'
    collection_name = 'unitactivities'


class Units(CollectionView):
    route_base      = 'units'
    collection_name = 'units'
    results_only    = True


class Lessons(CollectionView):
    route_base      = 'lessons'
    collection_name = 'lessons'
    results_only    = True


class LessonActivities(CollectionView):
    route_base      = 'lesson-activities'
    collection_name = 'lessonactivities'


class LessonFeedbacks(CollectionView):
    route_base      = 'lesson-feedbacks'
    collection_name = 'lessonfeedbacks'


class LessonTrackers(CollectionView):
    route_base      = 'lesson-trackers'
    collection_name = 'lessontrackers'

class Resources(CollectionView):
    route_base      = 'resources'
    collection_name = 'resources'


class Glossaries(CollectionView):
    route_base      = 'glossaries'
    collection_name = 'glossaries'


class SavedLessons(CollectionView):
    route_base      = 'saved-lessons'
    collection_name = 'savedlessons'


class MetaSubjectAreas(MetacollectionView):
    route_base      = 'subject-areas'
    collection_name = 'metasubjectareas'


# Standards
# ------------------------------------------------------------------------------
class MetaNycssUnits(MetacollectionView):
    route_base      = 'standards-nycss-units'
    collection_name = 'metanycssunits'


class MetaNysssKeyIdeas(MetacollectionView):
    route_base      = 'standards-nysss-key-ideas'
    collection_name = 'metanyssskeyideas'


class MetaNysssMajorUnderstandings(MetacollectionView):
    route_base      = 'standards-nysss-major-understandings'
    collection_name = 'metanysssmajorunderstandings'


class MetaNysssMsts(MetacollectionView):
    route_base      = 'standards-nysss-msts'
    collection_name = 'metanysssmsts'


class MetaNgssCrossCuttingConcepts(MetacollectionView):
    route_base      = 'standards-ngss-cross-cutting-concepts'
    collection_name = 'metangsscrosscuttingconcepts'


class MetaNgssDisciplinaryCoreIdeas(MetacollectionView):
    route_base      = 'standards-ngss-disciplinary-core-ideas'
    collection_name = 'metangssdisciplinarycoreideas'


class MetaNgssScienceEngineeringPractices(MetacollectionView):
    route_base      = 'standards-ngss-science-engineering-practices'
    collection_name = 'metangssscienceengineeringpractices'


class MetaCclsElaScienceTechnicalSubjects(MetacollectionView):
    route_base      = 'standards-ccls-ela-science-technical-subjects'
    collection_name = 'metacclselasciencetechnicalsubjects'


class MetaCclsMathematics(MetacollectionView):
    route_base      = 'standards-ccls-mathematics'
    collection_name = 'metacclsmathematics'
