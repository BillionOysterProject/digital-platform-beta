from __future__ import absolute_import
from __future__ import unicode_literals
from werkzeug.exceptions import Forbidden
import re

# a set of (METHOD, REGEX) tuples denoting paths that are anonymously
# accessible.
ANONYMOUS_ROUTES = (
    # allow people to login, and know when they are/are not logged in
    # --------------------------------------------------------------------------
    ('POST', re.compile('^/api/auth/signin/?')),
    ('GET', re.compile('^/api/auth/signout/?')),
    ('GET', re.compile('^/api/users/me/?')),

    # permit public access to participating and prospective organizations
    # --------------------------------------------------------------------------
    ('GET', re.compile('^/api/.*-orgs/?')),
    ('GET', re.compile('^/api/teams/?')),

    # permit public access to curriculum data
    # --------------------------------------------------------------------------
    ('GET', re.compile('^/api/unit.*/?')),
    ('GET', re.compile('^/api/.*lesson.*/?')),
    ('GET', re.compile('^/api/glossaries/?')),

    # permit public access to restoration data
    # --------------------------------------------------------------------------
    ('GET', re.compile('^/api/expedition.*/?')),
    ('GET', re.compile('^/api/sites/?')),
    ('GET', re.compile('^/api/restoration-stations/?')),
    ('GET', re.compile('^/api/protocol-.*/?')),
    ('GET', re.compile('^/api/.*-organisms/?')),
    ('GET', re.compile('^/api/.*research.*/?')),

    # permit public access to various resources
    # --------------------------------------------------------------------------
    ('GET', re.compile('^/api/metrics/?')),
    ('GET', re.compile('^/api/events/?')),
)

ROUTES_BY_GROUP = {
    # admins can do anything
    # --------------------------------------------------------------------------
    'admin': (
        ('*', re.compile('.*')),
    ),

    # team leads
    # --------------------------------------------------------------------------
    'team-lead': (
        ('GET', re.compile('^/api/users/?')),
        ('GET', re.compile('^/api/teams/?')),
    ),
}


def verify_path_is_authorized(view, request):
    method = request.method.lower()
    path = request.path

    # shortcut for anonymous routes
    for ruleMethod, rulePath in ANONYMOUS_ROUTES:
        if ruleMethod.lower() == method or ruleMethod == '*':
            if rulePath.match(path):
                return True

    user = view.current_user

    if user:
        for role, rules in ROUTES_BY_GROUP.items():
            for ruleMethod, rulePath in rules:
                if user.has_role(role):
                    if ruleMethod == method or ruleMethod == '*':
                        if rulePath.match(path):
                            return True

    raise Forbidden('You are not authorized to access this resource.')
