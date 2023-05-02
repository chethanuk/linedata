import json
import math
import os
import random
import string
from dataclasses import dataclass
from pathlib import Path
from typing import List

import line_level_data_collection.s3_helper as s3_helper
from line_level_data_collection import time_util
from line_level_data_collection.config import ProjectConfig
from line_level_data_collection.data_update_event import DataEntryUpdateEventV2
from line_level_data_collection.db.data_entry_update_record import DataEntryUpdateRecordRecordDB


@dataclass
class S3ObjectCreatedEvent:
    bucket: str
    key: str


def aggregate_events_to_db(event, context):
    event = S3ObjectCreatedEvent(bucket=event['detail']['bucket']['name'], key=event['detail']['object']['key'])
    target_bucket = os.environ['S3_BUCKET']
    client = s3_helper.get_client('s3')

    # get object
    event_json = s3_helper.download_s3_file_and_load_content(client=client, bucket=event.bucket,
                                                             key=event.key)
    # validate object
    update_event: DataEntryUpdateEventV2 = DataEntryUpdateEventV2.from_dict(event_json)

    # put it in db
    config = ProjectConfig()
    db = DataEntryUpdateRecordRecordDB(config)
    db.append_record(update_event)


def get_random_string(length) -> str:
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


@dataclass
class DataEntryUpdateEventV2Bundle:
    capacity: int
    events: List[DataEntryUpdateEventV2]
    language: str

    def __post_init__(self):
        assert len(self.events) <= self.capacity, f"capacity: {self.capacity}, events length: {len(self.events)}"

    def file_name(self):
        if len(self.events) >= self.capacity:
            file_stem = str(math.floor(time_util.utc_datetime_now().timestamp())) + '_' + get_random_string(4)
        else:
            file_stem = 'latest'
        return f"{file_stem}.json"

    def remaining_capacity(self) -> int:
        return self.capacity - len(self.events)

    def is_full(self) -> bool:
        return self.remaining_capacity() == 0

    def add_new_data(self, events: List[DataEntryUpdateEventV2]):
        return DataEntryUpdateEventV2Bundle(capacity=self.capacity, events=self.events + events, language=self.language)


class AggregatorV2:
    def __init__(self, language: str, s3_client, s3_bucket: str, tmp_dir: Path):
        self.language = language
        self.s3_bucket = s3_bucket
        self.s3_client = s3_client
        self.tmp_dir = tmp_dir
        self.wip_file_key = f"{language}/latest.json.gzip"

    def retrieve_last_progress(self) -> [DataEntryUpdateEventV2]:
        # if there is latest.json: retrieve it, unzip it
        # if there is not, return an empty array
        key = self.wip_file_key
        file_exists = s3_helper.check_file_existence(client=self.s3_client, bucket=self.s3_bucket, key=key)
        if file_exists:
            file_path = self.tmp_dir / "random.json.gzip"
            result = s3_helper.load_gzip_file_from_s3(client=self.s3_client, key=key, file_path=file_path,
                                                      bucket=self.s3_bucket)
            return [DataEntryUpdateEventV2.from_dict(e) for e in result]
        else:
            return []

    def write_to_s3(self, bundle: DataEntryUpdateEventV2Bundle) -> None:
        file_name = bundle.file_name()
        key = f"{self.language}/{file_name}.gzip"
        s3_helper.save_json_to_s3_in_gzip_format(client=self.s3_client, bucket=self.s3_bucket, key=key,
                                                 json_content=[e.to_dict() for e in bundle.events])
        if bundle.is_full():
            # delte object won't fail if the object doesn't exist
            # https://stackoverflow.com/questions/30697746/why-does-s3-deleteobject-not-fail-when-the-specified-key-doesnt-exist
            self.s3_client.delete_object(Bucket=self.s3_bucket, Key=self.wip_file_key)


def write_events_to_s3(event, context):
    # load language from event
    language = os.environ['LANGUAGE']
    target_bucket = os.environ['S3_BUCKET']
    capacity = int(os.environ['CAPACITY'])

    # check if consolidation is needed
    config = ProjectConfig()
    db = DataEntryUpdateRecordRecordDB(config)
    count = db.count(language=language)
    need_processing = count > 0
    if not need_processing:
        return

    # if needed, load data from s3
    client = s3_helper.get_client('s3')
    aggregator = AggregatorV2(
        s3_client=client,
        s3_bucket=target_bucket,
        language=language,
        tmp_dir=Path("/tmp")
    )
    existing_events = aggregator.retrieve_last_progress()
    bundle = DataEntryUpdateEventV2Bundle(events=existing_events, capacity=capacity, language=language)

    # read db and update bundle
    def add_data_to_s3(cursor):
        events = db._get(language=language, limit=bundle.remaining_capacity(), cur=cursor)
        new_bundle = bundle.add_new_data(events)
        db._remove(events=events, cur=cursor)
        # commit the transaction after writing to s3
        aggregator.write_to_s3(bundle=new_bundle)

    db.with_transaction(add_data_to_s3)


def get_data_info(event, context):
    language = event['pathParameters']['language']
    target_bucket = os.environ['S3_BUCKET_V2']
    response = {
        "statusCode": 200,
        "body": json.dumps(
            {
                'bucket': target_bucket,
                'key': language,
                'timestamp': time_util.utc_timestamp_to_iso_string(time_util.utc_datetime_now())
            }
        )
    }
    return response
