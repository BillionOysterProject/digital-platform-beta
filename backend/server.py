#!./env/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
from bop import API
import os
import logging
from gevent.wsgi import WSGIServer
from flask_cors import CORS
from gevent import monkey
from raven.contrib.flask import Sentry


# apply gevent patches, which is always precarious and weird but Python ¯\_(ツ)_/¯
monkey.patch_all()

# set level on global logging instance
logging.getLogger('').setLevel(logging.INFO)

# instantiate the application
app = API('bop-digital-platform')

# setup Sentry error reporting (only works if SENTRY_DSN envvar is set)
sentry = Sentry(app, logging=True, level=logging.WARNING)

# setup CORS headers
CORS(app, resources={
    r'/api/*': {
        'origins': '*',
    },
})

# determin listen address and port
addr = os.environ.get('HTTP_HOST', '127.0.0.1')
port = int(os.environ.get('HTTP_PORT', 5000))

# perform application setup tasks (e.g.: register routes and connect to things)
app.setup()

if __name__ == '__main__':
    wsgi_mode = int(os.environ.get('WSGI', '0'))

    if not wsgi_mode:
        logging.warning('DEBUGGING {} on http://{}:{}'.format(app.name, addr, port))
        debug_mode = (os.environ.get('DEBUG', '').lower() == 'true')

        app.run(
            debug=debug_mode,
            host=addr,
            port=port
        )
    else:
        logging.info('Running {} on {}:{}'.format(app.name, addr, port))
        http_server = WSGIServer((addr, port), app.wsgi_app)
        http_server.serve_forever()
