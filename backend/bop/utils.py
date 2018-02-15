from __future__ import absolute_import
from __future__ import unicode_literals


def as_bool(value):
    return ('{}'.format(value).lower() in ['true', '1', 'yes'])
