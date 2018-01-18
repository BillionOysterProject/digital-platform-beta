#!./env/bin/python
from __future__ import absolute_import
from __future__ import unicode_literals
from bop import API
import os
import logging
from gevent.wsgi import WSGIServer


app = API('bop-digital-platform')
addr = os.environ.get('HTTP_HOST', '127.0.0.1')
port = int(os.environ.get('HTTP_PORT', 5000))

logging.warning('Running {} on http://{}:{}'.format(app.name, addr, port))

if __name__ == '__main__' and not int(os.environ.get('WSGI', '0')):
    app.run(debug=False, host=addr, port=port)
else:
    http_server = WSGIServer((addr, port), app)
    http_server.serve_forever()
