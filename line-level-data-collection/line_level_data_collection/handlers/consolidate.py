import os
import traceback

import line_level_data_collection.s3_helper as s3_helper
from line_level_data_collection.config import ProjectConfig
from line_level_data_collection.db.data_entry_record import DataEntryRecordRecordDB, DataEntryRecord


def consolidate_data(event, context):
    # get event
    key = event['detail']['object']['key']
    config = ProjectConfig()
    bucket = os.environ['S3_BUCKET']
    client = s3_helper.get_client('s3')
    json_payload = s3_helper.download_s3_file_and_load_content(
        client=client,
        bucket=bucket,
        key=key
    )
    if validate_event(json_payload):
        db = DataEntryRecordRecordDB(config)
        record = DataEntryRecord.from_event_json_payload(json_payload=json_payload, event=event)
        already_exists = db.create_record_if_not_exists(record=record)
        if already_exists:
            print(f'already_exists')
    else:
        print('error during validation!')


def validate_event(json_payload):
    # noinspection PyBroadException
    try:
        from openapi_client.model.data_entry import DataEntry
        _ = DataEntry(**json_payload)
        return True
    except Exception as e:
        print(traceback.format_exc())
        return False
