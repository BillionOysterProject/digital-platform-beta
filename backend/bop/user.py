from __future__ import absolute_import
from __future__ import unicode_literals
import pivot.exceptions


class User(dict):
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
                return User(cls._flatten_record(users.records[0]))
        except pivot.exceptions.RecordNotFound:
            pass

        # fallback to finding the user by their email address
        try:
            users = cls.collection.query('email/is:{}'.format(id_or_email))

            if len(users) == 1:
                return User(cls._flatten_record(users.records[0]))

        except pivot.exceptions.RecordNotFound:
            pass

        # default to nothing
        return None

    @classmethod
    def _flatten_record(cls, data):
        record = data.get('fields', {})
        record['id'] = data['id']
        return record

    @property
    def is_authenticated(self):
        return False

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self['id']
