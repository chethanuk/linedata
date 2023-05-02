import json
import os

import line_level_data_collection.s3_helper as s3_helper
from line_level_data_collection.time_util import utc_timestamp_to_iso_string


def handler(event, context):
    language = event['pathParameters']['language']
    s3_bucket = os.environ['S3_BUCKET']
    client = s3_helper.get_client('s3')
    paginator = client.get_paginator('list_object_versions')
    page_iterator = paginator.paginate(Bucket=s3_bucket, Prefix=language)
    entries = []
    for page in page_iterator:
        versions = page.get('Versions', [])
        for version in versions:
            if version['IsLatest']:
                entries.append(version_to_response_entry(version, bucket=s3_bucket))
    return {
        "statusCode": 200,
        "body": json.dumps({'entries': entries})
    }


def version_to_response_entry(version_dict: dict, bucket: str):
    return {
        'key': version_dict['Key'],
        'version': version_dict['VersionId'],
        'bucket': bucket,
        'last_modified': utc_timestamp_to_iso_string(version_dict['LastModified'])
    }
