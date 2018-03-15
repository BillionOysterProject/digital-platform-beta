from __future__ import absolute_import
from __future__ import unicode_literals
from werkzeug.exceptions import Forbidden
import re

# a set of (METHOD, REGEX) tuples denoting paths that are anonymously
# accessible.
ANONYMOUS_ROUTES = (
    # allow people to login
    # --------------------------------------------------------------------------
    ('POST', re.compile('^/api/auth/signin/?')),

    # allow anyone to discover who they are, or that they aren't logged in
    # --------------------------------------------------------------------------
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


def verify_path_is_authorized(view, request):
    method = request.method
    path = request.path

    # shortcut for anonymous routes
    for m, rx in ANONYMOUS_ROUTES:
        if m == method:
            if rx.match(path):
                return True

    user = view.current_user

    if user:
        return True

    raise Forbidden('You are not authorized to access this resource.')
