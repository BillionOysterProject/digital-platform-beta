#!./env/bin/python
from __future__ import absolute_import
from __future__ import unicode_literals
import sys
from rq import Connection, Worker

with Connection():
    qs = sys.argv[1:] or ['default']

    w = Worker(qs)
    w.work()
