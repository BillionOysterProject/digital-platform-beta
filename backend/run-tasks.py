#!./env/bin/python
from __future__ import absolute_import
from __future__ import unicode_literals
from rq import Queue
from redis import Redis

redis_conn = Redis()
q = Queue(connection=redis_conn)

q.enqueue('bop.tasks.data.generate_batch_expeditions_tsv', timeout=600)

