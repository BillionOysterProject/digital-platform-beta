from __future__ import absolute_import
from __future__ import unicode_literals
import re
import pivot.exceptions
import base64
from pbkdf2 import PBKDF2


class User(dict):
    SENTRY_USER_ATTRS = ['username', 'email']

    def __init__(self, data):
        super(User, self).__init__(data)

    @classmethod
    def get(cls, id_or_email):
        # attempt to load the user by ID
        try:
            return User(cls.collection.get(id_or_email))
        except pivot.exceptions.RecordNotFound:
            pass

        # then try loading user by username
        try:
            users = cls.collection.query('username/is:{}'.format(id_or_email))

            if len(users) == 1:
                return User(users.records[0])
        except pivot.exceptions.RecordNotFound:
            pass

        # fallback to finding the user by their email address
        try:
            users = cls.collection.query('email/is:{}'.format(id_or_email))

            if len(users) == 1:
                return User(users.records[0])

        except pivot.exceptions.RecordNotFound:
            pass

        # default to nothing
        return None

    def check_password(self, password):
        salt = base64.b64decode(self['salt'])
        pwhash = base64.b64decode(self['password'])

        # NOTE: uses default SHA1 digest, which is insecure
        #       need to implement transparent rehashing on login to
        #       switch to a stronger digest algo.
        kdf = PBKDF2(password, salt, iterations=10000)
        out = kdf.read(64)

        if pwhash == out:
            return True

        return False

    @property
    def is_authenticated(self):
        return False

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def has_any_role(self, *roles):
        for role in roles:
            if self.has_role(role):
                return True

        return False

    def has_role(self, role):
        try:
            for r in self['roles']:
                if self._normalize_role(r) == self._normalize_role(role):
                    return True
        except KeyError:
            pass

        return False

    def get_id(self):
        return self['id']

    def _normalize_role(self, role):
        return re.sub(r'[\s\W\_]+', '-', '{}'.format(role)).lower()
