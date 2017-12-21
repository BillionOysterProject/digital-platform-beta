from __future__ import absolute_import
from __future__ import unicode_literals
from flask import jsonify
from .endpoints import Endpoint


class Metrics(Endpoint):
    def basic(self):
        return jsonify({
            "userCount": 1890,
            "teamCount": 619,
            "teamLeadCount": 485,
            "teamMemberCount": 677,
            "teacherCount": 331,
            "orgCount": 320,
            "expeditionCount": 324,
            "publishedExpeditionCount": 127,
            "activeStationCount": 162,
            "unitCount": 10,
            "lessonCount": 89,
            "taughtStudentCount": 1558,
            "pastEventCount": 40,
            "eventRegistrantTotal": 771,
            "currentEventCount": 2
        })
