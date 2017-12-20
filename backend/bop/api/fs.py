from __future__ import absolute_import
from __future__ import unicode_literals
from .endpoints import CollectionView


class FsChunks(CollectionView):
    route_prefix    = '/api/fs.chunks/'
    collection_name = 'fs.chunks'


class FsFiles(CollectionView):
    route_prefix    = '/api/fs.files/'
    collection_name = 'fs.files'
