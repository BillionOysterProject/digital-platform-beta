#!./env/bin/python
from __future__ import absolute_import
from __future__ import unicode_literals
from bop import API
import os
import logging
from gevent.wsgi import WSGIServer
from flask_cors import CORS

app = API('bop-digital-platform')

CORS(app, resources={
    r'/api/*': {
        'origins': '*',
    },
})

addr = os.environ.get('HTTP_HOST', '127.0.0.1')
port = int(os.environ.get('HTTP_PORT', 5000))

logging.warning('Running {} on http://{}:{}'.format(app.name, addr, port))

if __name__ == '__main__' and not int(os.environ.get('WSGI', '0')):
    debug_mode = (os.environ.get('DEBUG', '').lower() == 'true')

    app.run(
        debug=debug_mode,
        host=addr,
        port=port
    )
else:
    http_server = WSGIServer((addr, port), app)
    http_server.serve_forever()
