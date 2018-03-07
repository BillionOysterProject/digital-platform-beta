from __future__ import absolute_import
from __future__ import unicode_literals
from .endpoints import CollectionView


class UnitActivities(CollectionView):
    route_base      = 'unit-activities'
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
        ),
        'lessons': (
            'lessons', ['_id', 'status', 'title'],
        ),
    }


class Lessons(CollectionView):
    route_base      = 'lessons'
    collection_name = 'lessons'
    results_only    = True
    expand_fields   = {
        'user': (
            'users', ['_id', 'displayName', 'email'],
        ),
        'lessonOverview.subjectAreas': (
            'metasubjectareas', [],
        ),
        'unit': (
            'units', ['_id', 'title', 'color', 'icon'],
        ),
        'units': (
            'units', ['_id', 'title', 'color', 'icon'],
        ),
        'standards.cclsElaScienceTechnicalSubjects': (
            'metacclselasciencetechnicalsubjects', [],
        ),
        'standards.cclsMathematics': (
            'metacclsmathematics', [],
        ),
        'standards.ngssCrossCuttingConcepts': (
            'metangsscrosscuttingconcepts', [],
        ),
        'standards.ngssDisciplinaryCoreIdeas': (
            'metangssdisciplinarycoreideas', [],
        ),
        'standards.ngssScienceEngineeringPractices': (
            'metangssscienceengineeringpractices', [],
        ),
        'standards.nycsssUnits': (
            'metanycssunits', [],
        ),
        'standards.nysssKeyIdeas': (
            'metanyssskeyideas', [],
        ),
        'standards.nysssMajorUnderstandings': (
            'metanysssmajorunderstandings', [],
        ),
        'standards.nysssMst': (
            'metanysssmsts', [],
        ),
    }


class LessonActivities(CollectionView):
    route_base      = 'lesson-activities'
    collection_name = 'lessonactivities'


class LessonFeedbacks(CollectionView):
    route_base      = 'lesson-feedbacks'
    collection_name = 'lessonfeedbacks'


class LessonTrackers(CollectionView):
    route_base      = 'lesson-trackers'
    collection_name = 'lessontrackers'


class Glossaries(CollectionView):
    route_base      = 'glossaries'
    collection_name = 'glossaries'


class SavedLessons(CollectionView):
    route_base      = 'saved-lessons'
    collection_name = 'savedlessons'
