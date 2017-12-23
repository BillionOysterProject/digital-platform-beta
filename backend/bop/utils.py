from __future__ import absolute_import


def as_bool(value):
    return ('{}'.format(value).lower() in ['true', '1', 'yes'])
