import json
import os

import boto3

from line_level_data_collection.config import project_root
from line_level_data_collection.s3_helper import get_client
from line_level_data_collection.handlers.snapshot import handler
from line_level_data_collection.test_util import FakeContext

read_bucket_name = 'data-entry-bucket'


def setup_function(fun):
    os.environ['S3_BUCKET'] = read_bucket_name
    print("in setup function: " + fun.__name__)

    client = get_client("s3")
    client.create_bucket(
        Bucket=read_bucket_name,
        CreateBucketConfiguration={'LocationConstraint': 'eu-west-2'}
    )
    s3 = boto3.resource('s3', endpoint_url=os.environ["AWS_MOCK_URL"])
    versioning = s3.BucketVersioning(read_bucket_name)
    versioning.enable()


def teardown_function(function):
    print(f"teardown function for {function.__name__}")
    del os.environ['S3_BUCKET']

    client = get_client('s3')
    paginator = client.get_paginator('list_object_versions')
    response_iterator = paginator.paginate(Bucket=read_bucket_name)
    for response in response_iterator:
        versions = response.get('Versions', [])
        versions.extend(response.get('DeleteMarkers', []))
        for version in versions:
            client.delete_object(Bucket=read_bucket_name, Key=version['Key'], VersionId=version['VersionId'])

    s3 = boto3.resource('s3', endpoint_url=os.environ["AWS_MOCK_URL"])
    bucket = s3.Bucket(read_bucket_name)
    bucket.delete()


def test_snapshot_with_entries():
    test_data_dir = project_root / "tests/resources"

    client = get_client("s3")
    for i in range(10):
        data_entry_file = test_data_dir / "sample_approval_event.json"
        client.upload_file(
            Filename=str(data_entry_file),
            Bucket=read_bucket_name,
            Key=f"math/sample_object_{i}"
        )
        # the api should only return latest version, older version should not be returned
        null_event_file = test_data_dir / "null_event.json"
        client.upload_file(
            Filename=str(data_entry_file),
            Bucket=read_bucket_name,
            Key=f"math/sample_object_{i}"
        )

        client.upload_file(
            Filename=str(data_entry_file),
            Bucket=read_bucket_name,
            Key=f"other_languages/sample_object_{i}"
        )
        # the api should only return latest version, deleted version shouldn't be returned
        if i % 2 == 0:
            client.delete_object(Bucket=read_bucket_name, Key=f"math/sample_object_{i}")

    event = {
        'pathParameters': {
            'language': 'math'
        }
    }
    response = handler(event, FakeContext())
    entries = json.loads(response['body'])['entries']
    assert len(entries) == 5
    for entry in entries:
        assert 'key' in entry
        assert 'version' in entry
        assert entry['bucket'] == read_bucket_name
        assert 'last_modified' in entry


def test_snapshot_without_entries():
    event = {
        'pathParameters': {
            'language': 'math'
        }
    }
    response = handler(event, FakeContext())
    entries = json.loads(response['body'])['entries']
    assert len(entries) == 0
