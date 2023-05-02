import json
import os

import boto3

from line_level_data_collection.config import ProjectConfig, project_root

from line_level_data_collection.db.data_entry_record import DataEntryRecordRecordDB
from line_level_data_collection.handlers.consolidate import consolidate_data
from line_level_data_collection.s3_helper import get_client
from line_level_data_collection.test_util import FakeContext
from line_level_data_collection.test_util.testdb import DatabaseTestingHelper

read_bucket_name = 'data-s3-bucket'


def setup_function(fun):
    os.environ['S3_BUCKET'] = read_bucket_name
    print("in setup function: " + fun.__name__)
    # clean db
    tables = [
        "data_entry"
    ]
    for table in tables:
        DatabaseTestingHelper(ProjectConfig("test")).clean_db(table_name=table)

    #### prepare s3
    s3 = get_client("s3")
    s3.create_bucket(
        Bucket=read_bucket_name,
        CreateBucketConfiguration={'LocationConstraint': 'eu-west-2'}
    )

    test_data_dir = project_root / "tests/resources"
    data_entry_file = test_data_dir / "data_entry.json"
    s3.upload_file(
        Filename=str(data_entry_file),
        Bucket=read_bucket_name,
        Key="d507a8a1-9973-4e8b-ab14-f1758efb8209"
    )


def teardown_function(function):
    del os.environ['S3_BUCKET']
    print(f"teardown function for {function.__name__}")
    s3 = boto3.resource('s3', endpoint_url=os.environ["AWS_MOCK_URL"])
    bucket = s3.Bucket(read_bucket_name)
    bucket.objects.all().delete()
    bucket.delete()

    # clean db
    tables = [
        "data_entry"
    ]
    for table in tables:
        DatabaseTestingHelper(ProjectConfig("test")).clean_db(table_name=table)


def test_lambda_handler():
    db = DataEntryRecordRecordDB(ProjectConfig("test"))
    count = db.count()
    assert count == 0

    event_path = project_root / "tests/resources/event_bridge_s3_event.json"
    with event_path.open(mode="r") as f:
        event = json.loads(f.read())

    consolidate_data(event=event, context=FakeContext())

    count = db.count()
    assert count == 1
