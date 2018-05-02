#!./env/bin/python
from __future__ import absolute_import
from __future__ import unicode_literals
import sys
from rq import Connection, Worker
from raven import Client


sentry = Client()

try:
    with Connection():
        qs = sys.argv[1:] or ['default']

        w = Worker(qs)
        w.work()
except:
    sentry.captureException()
    raise