from __future__ import absolute_import
from __future__ import unicode_literals
import os
from .endpoints import Endpoint, CollectionView, GeoCollectionView
from flask import jsonify, request, g, redirect
from werkzeug.exceptions import BadRequest, Unauthorized
from flask_classy import route
from flask_login import login_user, logout_user
from ..utils import as_bool
from ..user import User
import six
import os
import logging
import pivot.exceptions


class Authentication(Endpoint):
    route_base = 'auth'

    @route('/signin', methods=['POST'])
    def signin(self):
        if len(request.form):
            payload = request.form
        else:
            payload = request.get_json(force=True)

        user = User.get(payload['username'])

        if not user:
            raise Unauthorized('Invalid username or password.')

        if 'password' not in payload:
            raise Unauthorized('Invalid username or password.')

        if not isinstance(payload['password'], six.string_types):
            raise Unauthorized('Invalid username or password.')

        if user.check_password(payload['password']):
            login_user(user, remember=True)

            return jsonify(user)
        else:
            raise Unauthorized('Invalid username or password.')

    def signout(self):
        logout_user()
        return ('', 204)


class TeamRequests(CollectionView):
    route_base      = 'teamrequests'
    collection_name = 'teamrequests'


class Teams(CollectionView):
    route_base      = 'teams'
    collection_name = 'teams'
    results_only    = True

    def index(self):
        """
        Retrieve a list of teams, optionally filtered by various criteria.

        + Parameters
            + byOwner: `false` (bool) -
                Limit results to only teams the current user leads.

            + byMember: `false` (bool) -
                Limit results to only teams the current user is a member of.

            + orgId: `abc123` (string) -
                Limit results to only teams belonging to the given organization.

            + userId: `1234` (string) -
                Specify a user ID for the byOwner and byMember options in lieu of
                the currently logged in user.
        """
        user_id = request.args.get('userId', g.get('user_id'))
        basequery = request.args.get('q')
        query = []

        if as_bool(request.args.get('byOwner')):
            query.append('teamLeads/{}'.format(user_id))

        if as_bool(request.args.get('byMember')):
            query.append('teamMembers/{}'.format(user_id))

        # TODO: implement field OR field
        # if as_bool(request.args.get('teamsImOn')):
        #     query.append('teamMembers|teamLeads/{}'.format(user_id))

        if request.args.get('orgId'):
            query.append('schoolOrg/{}'.format(
                request.args['orgId']
            ))

        if basequery:
            query = [basequery] + query

        if len(query):
            g.query = '/'.join(query)

        return super(Teams, self).index()


class UserActivities(CollectionView):
    route_base      = 'useractivities'
    collection_name = 'useractivities'


def _load_user(id_or_email):
    return User.get(id_or_email)


class Users(CollectionView):
    route_base      = 'users'
    collection_name = 'users'

    @classmethod
    def register(cls, app):
        super(Users, cls).register(app)
        app.login_manager.user_loader(_load_user)
        User.collection = cls.get_collection()

    @property
    def current_user(self):
        impersonate = os.getenv('IMPERSONATE')

        if impersonate == 'off':
            impersonate = None

        if impersonate:
            # try loading the IMPERSONATE user
            try:
                users = self.collection.query('username/is:{}'.format(impersonate))

                if len(users) == 1:
                    logging.warning('Impersonating user {}'.format(impersonate))
                    return User(users.records[0])
            except pivot.exceptions.RecordNotFound:
                pass

        else:
            return super(Users, self).current_user

    def me(self):
        user = self.current_user

        if user:
            return jsonify(user)
        else:
            raise Unauthorized('Not logged in.')

    def teamleads(self):
        basequery = request.args.get('q')
        query = ['roles/team lead']

        if basequery:
            query = [basequery] + query

        if len(query):
            g.query = '/'.join(query)

        return super(Users, self).index()


class Sessions(CollectionView):
    route_base      = 'sessions'
    collection_name = 'sessions'


class SchoolOrgs(GeoCollectionView):
    route_base      = 'school-orgs'
    collection_name = 'schoolorgs'

    def index(self):
        """
        Retrieve a list of schools/organizations, optionally filtered by various criteria.

        + Parameters
            + approvedOnly: `false` (bool) -
                Limit results to only organizations that have been approved.
        """
        basequery = request.args.get('q')
        query = []

        if as_bool(request.args.get('approvedOnly')):
            query.append('bool:pending/false')

        if basequery:
            query = [basequery] + query

        if len(query):
            g.query = '/'.join(query)

        return super(SchoolOrgs, self).index()


class ProspectiveOrgs(GeoCollectionView):
    route_base      = 'prospective-orgs'
    collection_name = 'prospectiveorgs'
