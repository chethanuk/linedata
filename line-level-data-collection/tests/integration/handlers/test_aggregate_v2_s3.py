import os
import tempfile
from pathlib import Path

import boto3

from line_level_data_collection import s3_helper
from line_level_data_collection.data_update_event import DataEntryUpdateEventV2
from line_level_data_collection.handlers.aggregate_v2 import AggregatorV2, DataEntryUpdateEventV2Bundle
from line_level_data_collection.s3_helper import get_client
from line_level_data_collection.test_util import generate_update_record

bucket = 'test-bucket'


def setup_function(fun):
    print("in setup function: " + fun.__name__)
    s3 = get_client("s3")
    s3.create_bucket(
        Bucket=bucket,
        CreateBucketConfiguration={'LocationConstraint': 'eu-west-2'}
    )


def teardown_function(function):
    print(f"teardown function for {function.__name__}")
    s3 = boto3.resource('s3', endpoint_url=os.environ["AWS_MOCK_URL"])

    s3_bucket = s3.Bucket(bucket)
    s3_bucket.objects.all().delete()
    s3_bucket.delete()


def test_aggregator_v2_write_and_get_events_not_full():
    lang = 'lang'
    aggregator = AggregatorV2(language=lang, s3_client=get_client('s3'), s3_bucket=bucket, tmp_dir=Path('/tmp'))
    data = [generate_update_record() for _ in range(6)]
    bundle = DataEntryUpdateEventV2Bundle(capacity=10, events=data, language=lang)
    aggregator.write_to_s3(bundle)


def test_aggregator_v2_write_and_get_events_not_full_2():
    lang = 'lang'
    aggregator = AggregatorV2(language=lang, s3_client=get_client('s3'), s3_bucket=bucket, tmp_dir=Path('/tmp'))
    data = [generate_update_record() for _ in range(6)]
    bundle = DataEntryUpdateEventV2Bundle(capacity=10, events=data, language=lang)
    aggregator.write_to_s3(bundle)
    retrieved = aggregator.retrieve_last_progress()
    assert retrieved == data

    # count object
    s3 = boto3.resource('s3', endpoint_url=os.environ["AWS_MOCK_URL"])
    s3_bucket = s3.Bucket(bucket)
    all_objects = list(s3_bucket.objects.all())
    count = len(all_objects)

    # the object should be named latest.xxxx
    assert count == 1
    assert any(['latest' in e.key for e in all_objects])

    # check the content of the s3 object
    key = all_objects[0].key
    with tempfile.TemporaryDirectory() as tmp_dirname:
        result = s3_helper.load_gzip_file_from_s3(client=get_client("s3"), key=key,
                                                  file_path=Path(tmp_dirname) / "sth.json.gzip", bucket=bucket)
    assert [DataEntryUpdateEventV2.from_dict(e) for e in result] == bundle.events


def test_aggregator_v2_write_and_get_events_full():
    lang = 'lang'
    aggregator = AggregatorV2(language=lang, s3_client=get_client('s3'), s3_bucket=bucket, tmp_dir=Path('/tmp'))
    data = [generate_update_record() for _ in range(6)]
    bundle = DataEntryUpdateEventV2Bundle(capacity=6, events=data, language=lang)
    aggregator.write_to_s3(bundle)
    retrieved = aggregator.retrieve_last_progress()
    assert retrieved == []

    # count object
    s3 = boto3.resource('s3', endpoint_url=os.environ["AWS_MOCK_URL"])
    s3_bucket = s3.Bucket(bucket)
    all_objects = list(s3_bucket.objects.all())
    count = len(all_objects)

    # the object should not be named latest.xxxx
    assert count == 1
    assert not any(['latest' in e.key for e in all_objects])

    # check the content of the s3 object
    key = all_objects[0].key
    with tempfile.TemporaryDirectory() as tmp_dirname:
        result = s3_helper.load_gzip_file_from_s3(client=get_client("s3"), key=key,
                                                  file_path=Path(tmp_dirname) / "sth.json.gzip", bucket=bucket)
    assert [DataEntryUpdateEventV2.from_dict(e) for e in result] == bundle.events


def test_aggregator_v2_write_and_get_events_default():
    lang = 'lang'
    aggregator = AggregatorV2(language=lang, s3_client=get_client('s3'), s3_bucket=bucket, tmp_dir=Path('/tmp'))
    retrieved = aggregator.retrieve_last_progress()
    assert retrieved == []


def test_aggregator_v2_clean_up_wip_file_when_full():
    lang = 'lang'
    aggregator = AggregatorV2(language=lang, s3_client=get_client('s3'), s3_bucket=bucket, tmp_dir=Path('/tmp'))

    # there is a half-full bundle in s3. should be using the name latest.xxxx
    data = [generate_update_record() for _ in range(3)]
    bundle = DataEntryUpdateEventV2Bundle(capacity=6, events=data, language=lang)
    aggregator.write_to_s3(bundle)

    # try to make it full
    data2 = [generate_update_record() for _ in range(3)]
    bundle2 = bundle.add_new_data(data2)
    aggregator.write_to_s3(bundle2)

    # count object
    s3 = boto3.resource('s3', endpoint_url=os.environ["AWS_MOCK_URL"])
    s3_bucket = s3.Bucket(bucket)
    all_objects = list(s3_bucket.objects.all())
    count = len(all_objects)

    # there should be one object as latest.xxx is removed
    assert count == 1
    assert not any(['latest' in e.key for e in all_objects])

    # check the content of the s3 object
    key = all_objects[0].key
    with tempfile.TemporaryDirectory() as tmp_dirname:
        result = s3_helper.load_gzip_file_from_s3(client=get_client("s3"), key=key,
                                                  file_path=Path(tmp_dirname) / "sth.json.gzip", bucket=bucket)
    assert [DataEntryUpdateEventV2.from_dict(e) for e in result] == bundle2.events
