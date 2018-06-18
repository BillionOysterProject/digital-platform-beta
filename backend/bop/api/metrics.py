from __future__ import absolute_import
from __future__ import unicode_literals
from flask import jsonify
from .endpoints import Endpoint
from ..time import Time


class Metrics(Endpoint):
    def basic(self):
        users        = self.collection_for('users')
        teams        = self.collection_for('teams')
        orgs         = self.collection_for('schoolorgs')
        expeditions  = self.collection_for('expeditions')
        stations     = self.collection_for('restorationstations')
        units        = self.collection_for('units')
        lessons      = self.collection_for('lessons')
        trackers     = self.collection_for('lessontrackers')
        events       = self.collection_for('calendarevents')
        now          = Time()

        return jsonify({
            'userCount':                users.count(),
            'teamCount':                teams.count(),
            'teamLeadCount':            users.count('roles/team lead|team lead pending|admin'),
            'teamMemberCount':          users.count('roles/team member|team member pending'),
            'teacherCount':             users.count('teamLeadType/teacher'),
            'orgCount':                 orgs.count(),
            'expeditionCount':          expeditions.count(),
            'publishedExpeditionCount': expeditions.count('status/published'),
            'activeStationCount':       stations.count('status/Active'),
            'unitCount':                units.count(),
            'lessonCount':              lessons.count(),
            'taughtStudentCount':       trackers.sum('totalNumberOfStudents'),
            'pastEventCount':           events.count('dates.startDateTime/lt:{}'.format(now)),
            'currentEventCount':        events.count('dates.startDateTime/gte:{}'.format(now)),
            'eventRegistrantTotal':     -1,
        })
