from __future__ import absolute_import
from __future__ import unicode_literals
import os


def get_reports_bucket():
    if 'BOP_S3_PUBLIC_BUCKET' not in os.environ:
        raise Exception(
            'Must specify the bucket to put results in with BOP_S3_PUBLIC_BUCKET envvar.'
        )

    # verify the destination bucket exists, or throw an exception before processing
    return os.environ['BOP_S3_PUBLIC_BUCKET']
