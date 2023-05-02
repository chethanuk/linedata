import copy
import json
import os

import boto3

from line_level_data_collection.config import ProjectConfig, project_root
from line_level_data_collection.data_update_event import DataEntryUpdateEvent, DataEntryUpdateEventV2
from line_level_data_collection.db.data_entry_record import DataEntryRecordRecordDB, ApprovalStatus
from line_level_data_collection.handlers.verification import update_data_entry
from line_level_data_collection.s3_helper import get_client
from line_level_data_collection.test_util import FakeContext, generate_entry_record
from line_level_data_collection.test_util.testdb import DatabaseTestingHelper

update_event_bucket = 'data-s3-bucket'
update_event_bucket_v2 = 'data-s3-bucket-v2'


def setup_function(fun):
    os.environ['S3_BUCKET'] = update_event_bucket
    os.environ['S3_BUCKET_V2'] = update_event_bucket_v2
    print("in setup function: " + fun.__name__)
    # clean db
    tables = [
        "data_entry"
    ]
    for table in tables:
        DatabaseTestingHelper(ProjectConfig("test")).clean_db(table_name=table)

    #### prepare s3
    s3 = get_client("s3")
    buckets = [update_event_bucket, update_event_bucket_v2]
    for bucket in buckets:
        s3.create_bucket(
            Bucket=bucket,
            CreateBucketConfiguration={'LocationConstraint': 'eu-west-2'}
        )


def teardown_function(function):
    del os.environ['S3_BUCKET']
    del os.environ['S3_BUCKET_V2']
    print(f"teardown function for {function.__name__}")
    s3 = boto3.resource('s3', endpoint_url=os.environ["AWS_MOCK_URL"])
    buckets = [update_event_bucket, update_event_bucket_v2]
    for bucket in buckets:
        bucket = s3.Bucket(bucket)
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
    record0 = generate_entry_record(language="lang1", approval_status=ApprovalStatus.UNPROCESSED)
    db.create_record_if_not_exists(record=record0)

    event_path = project_root / "tests/resources/update_entry_event.json"
    with event_path.open(mode="r") as f:
        event = json.loads(f.read())

    event['pathParameters']['id'] = str(record0.id)

    update_data_entry(event=event, context=FakeContext())

    # verify the status is updated
    retrieved = db.find_one_by_id(id=record0.id)
    expected = copy.deepcopy(record0)
    expected.approval_status = ApprovalStatus.APPROVED
    assert retrieved.content_equal(expected)

    # verify s3 object is created
    # verify s3 object has the content I expect. V1
    s3 = boto3.resource('s3', endpoint_url=os.environ["AWS_MOCK_URL"])
    bucket = s3.Bucket(update_event_bucket)
    keys = [my_bucket_object.key for my_bucket_object in bucket.objects.all()]
    assert len(keys) == 1

    s3 = get_client("s3")
    result = s3.get_object(Bucket=update_event_bucket, Key=keys[0])
    decoded = result["Body"].read().decode()

    actual_event = DataEntryUpdateEvent.from_json(decoded)
    expected_event = DataEntryUpdateEvent.from_data_entry_record(data_entry_record=expected)
    assert expected_event.content_equal(actual_event)

    # verify s3 object has the content I expect. V2
    s3 = boto3.resource('s3', endpoint_url=os.environ["AWS_MOCK_URL"])
    bucket = s3.Bucket(update_event_bucket_v2)
    keys = [my_bucket_object.key for my_bucket_object in bucket.objects.all()]
    assert len(keys) == 1

    s3 = get_client("s3")
    result = s3.get_object(Bucket=update_event_bucket_v2, Key=keys[0])
    decoded = result["Body"].read().decode()

    actual_event = DataEntryUpdateEventV2.from_json(decoded)
    expected_event = DataEntryUpdateEventV2.from_data_entry_record(data_entry_record=expected)
    assert expected_event.content_equal(actual_event)
