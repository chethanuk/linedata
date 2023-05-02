import json
import os
import tempfile
from pathlib import Path

import boto3

from line_level_data_collection.config import project_root
from line_level_data_collection.handlers.aggregate import aggregate_events

from line_level_data_collection.s3_helper import get_client, load_gzip_file_from_s3, save_json_to_s3_in_gzip_format
from line_level_data_collection.test_util import FakeContext

read_bucket_name = 'lldc-qa-data-entry-event20230220113044668400000001'
write_bucket_name = 'aggregation-bucket'


def setup_function(fun):
    os.environ['S3_BUCKET'] = write_bucket_name
    print("in setup function: " + fun.__name__)

    #### prepare s3
    s3 = get_client("s3")
    s3.create_bucket(
        Bucket=read_bucket_name,
        CreateBucketConfiguration={'LocationConstraint': 'eu-west-2'}
    )

    s3.create_bucket(
        Bucket=write_bucket_name,
        CreateBucketConfiguration={'LocationConstraint': 'eu-west-2'}
    )

    test_data_dir = project_root / "tests/resources"
    data_entry_file = test_data_dir / "sample_approval_event.json"
    s3.upload_file(
        Filename=str(data_entry_file),
        Bucket=read_bucket_name,
        Key="023d86e4-2ff5-4239-a814-b49a07352b34"
    )


def teardown_function(function):
    print(f"teardown function for {function.__name__}")

    del os.environ['S3_BUCKET']
    s3 = boto3.resource('s3', endpoint_url=os.environ["AWS_MOCK_URL"])
    bucket = s3.Bucket(read_bucket_name)
    bucket.objects.all().delete()
    bucket.delete()

    bucket = s3.Bucket(write_bucket_name)
    bucket.objects.all().delete()
    bucket.delete()


def test_lambda_handler_no_latest_file():
    os.environ['CAPACITY'] = '5000'
    event_path = project_root / "tests/resources/event_bridge_s3_event_approval_events.json"
    with event_path.open(mode="r") as f:
        event = json.loads(f.read())
    aggregate_events(event=event, context=FakeContext())
    with tempfile.TemporaryDirectory() as tmp_dirname:
        file_path = Path(tmp_dirname) / "temp.json"
        content = load_gzip_file_from_s3(get_client("s3"), bucket=write_bucket_name, key='math/latest.json.gzip',
                                         file_path=file_path)
    assert len(content) == 1

    test_data_dir = project_root / "tests/resources"
    data_entry_file = test_data_dir / "sample_approval_event.json"
    with data_entry_file.open(mode='r') as f:
        update_event = json.load(f)
    assert content == [update_event]

    # test file key
    s3 = boto3.resource('s3', endpoint_url=os.environ["AWS_MOCK_URL"])
    bucket = s3.Bucket(write_bucket_name)
    objects = list(bucket.objects.all())
    assert len(objects) == 1
    assert objects[0].key == 'math/latest.json.gzip'


def test_lambda_handler_reach_capacity():
    # preparation
    os.environ['CAPACITY'] = '20'
    test_data_dir = project_root / "tests/resources"
    data_entry_file = test_data_dir / "sample_approval_event.json"
    with data_entry_file.open(mode='r') as f:
        update_event = json.load(f)

    # upload previous_approvals
    previous_approvals = [update_event for _ in range(19)]
    save_json_to_s3_in_gzip_format(get_client('s3'), bucket=write_bucket_name, key='math/latest.json.gzip',
                                   json_content=previous_approvals)

    event_path = project_root / "tests/resources/event_bridge_s3_event_approval_events.json"
    with event_path.open(mode="r") as f:
        event = json.loads(f.read())
    aggregate_events(event=event, context=FakeContext())

    # test file key
    s3 = boto3.resource('s3', endpoint_url=os.environ["AWS_MOCK_URL"])
    bucket = s3.Bucket(write_bucket_name)
    object_summaries = list(bucket.objects.all())
    assert len(object_summaries) == 1

    # make sure the name contains only numbers
    s3_object = object_summaries[0]
    int(Path(s3_object.key).name.split('.')[0])

    # make sure content is correct
    with tempfile.TemporaryDirectory() as tmp_dirname:
        file_path = Path(tmp_dirname) / "temp.json"
        content = load_gzip_file_from_s3(get_client('s3'), bucket=s3_object.bucket_name,
                                         key=s3_object.key, file_path=file_path)

    expected = previous_approvals + [update_event]
    assert content == expected

    # test read bucket object is removed
    s3 = boto3.resource('s3', endpoint_url=os.environ["AWS_MOCK_URL"])
    bucket = s3.Bucket(read_bucket_name)
    object_summaries = list(bucket.objects.all())
    assert len(object_summaries) == 0


def test_lambda_handler_not_reach_capacity():
    # preparation
    os.environ['CAPACITY'] = '20'
    test_data_dir = project_root / "tests/resources"
    data_entry_file = test_data_dir / "sample_approval_event.json"
    with data_entry_file.open(mode='r') as f:
        update_event = json.load(f)

    # upload previous_approvals
    previous_approvals = [update_event for _ in range(10)]
    save_json_to_s3_in_gzip_format(get_client('s3'), bucket=write_bucket_name, key='math/latest.json.gzip',
                                   json_content=previous_approvals)

    event_path = project_root / "tests/resources/event_bridge_s3_event_approval_events.json"
    with event_path.open(mode="r") as f:
        event = json.loads(f.read())
    aggregate_events(event=event, context=FakeContext())

    # test file key
    s3 = boto3.resource('s3', endpoint_url=os.environ["AWS_MOCK_URL"])
    bucket = s3.Bucket(write_bucket_name)
    object_summaries = list(bucket.objects.all())
    assert len(object_summaries) == 1

    s3_object = object_summaries[0]
    assert s3_object.key == "math/latest.json.gzip"

    # make sure content is correct
    with tempfile.TemporaryDirectory() as tmp_dirname:
        file_path = Path(tmp_dirname) / "temp.json"
        content = load_gzip_file_from_s3(get_client('s3'), bucket=s3_object.bucket_name,
                                         key=s3_object.key, file_path=file_path)

    expected = previous_approvals + [update_event]
    assert content == expected

    # test read bucket object is removed
    s3 = boto3.resource('s3', endpoint_url=os.environ["AWS_MOCK_URL"])
    bucket = s3.Bucket(read_bucket_name)
    object_summaries = list(bucket.objects.all())
    assert len(object_summaries) == 0
