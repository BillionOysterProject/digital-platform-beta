#!./env/bin/python
from __future__ import absolute_import
from __future__ import unicode_literals
from bop import API

app = API('bop-digital-platform')


if __name__ == '__main__':
    app.run(debug=True)
