from __future__ import absolute_import
from __future__ import unicode_literals


def echo(*args):
    print(' '.join([
        '{}'.format(v) for v in args
    ]))
