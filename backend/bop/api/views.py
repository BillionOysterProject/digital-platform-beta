from __future__ import absolute_import
from __future__ import unicode_literals
from .endpoints import CollectionView


class Events(CollectionView):
    route_base      = 'events'
    collection_name = 'calendarevents'
    results_only    = True


class Circles(CollectionView):
    route_base      = 'circles'
    collection_name = 'circles'


class ResearchActivities(CollectionView):
    route_base      = 'research-activities'
    collection_name = 'researchactivities'


class Researches(CollectionView):
    route_base      = 'researches'
    collection_name = 'researches'


class ResearchFeedbacks(CollectionView):
    route_base      = 'research-feedbacks'
    collection_name = 'researchfeedbacks'


class SavedResearches(CollectionView):
    route_base      = 'saved-researches'
    collection_name = 'savedresearches'
