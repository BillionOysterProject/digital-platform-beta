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


class Glossaries(CollectionView):
    route_base      = 'glossaries'
    collection_name = 'glossaries'


class SavedLessons(CollectionView):
    route_base      = 'saved-lessons'
    collection_name = 'savedlessons'
