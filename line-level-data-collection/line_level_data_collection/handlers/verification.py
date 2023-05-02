import base64
import json
import os
import uuid

from psycopg2 import extensions

from line_level_data_collection.config import ProjectConfig
from line_level_data_collection.data_entry_view import DataEntryView
from line_level_data_collection.data_update_event import DataEntryUpdateEvent, DataEntryUpdateEventV2
from line_level_data_collection.db.data_entry_record import DataEntryRecordRecordDB, ApprovalStatus


def get_languages(event, context):
    config = ProjectConfig()
    db = DataEntryRecordRecordDB(config)
    languages = db.get_languages()
    return {"statusCode": 200, "body": json.dumps({"languages": languages})}


def update_data_entry(event, context):
    data_entry_id = uuid.UUID(event['pathParameters']['id'])

    config = ProjectConfig()
    db = DataEntryRecordRecordDB(config)

    def update_status(cursor: extensions.cursor):

        existing = db.find_one_by_id(id=data_entry_id)
        if existing is None:
            return {"statusCode": 404, "body": json.dumps({"msg": f"{str(data_entry_id)} is not found"})}

        body = json.loads(event["body"])
        updated_entry, is_changed = existing.update(update_data=body)

        if is_changed:
            db.update_data_entry(new_data_entry=updated_entry, cursor=cursor)

            import line_level_data_collection.s3_helper as s3_helper
            client = s3_helper.get_client('s3')
            bucket = os.environ['S3_BUCKET']

            json_object = DataEntryUpdateEvent.from_data_entry_record(data_entry_record=updated_entry).to_json()
            client.put_object(
                Body=json_object,
                Bucket=bucket,
                Key=f"{updated_entry.language}/f{str(uuid.uuid4())}"
            )

            bucket_v2 = os.environ['S3_BUCKET_V2']
            json_object = DataEntryUpdateEventV2.from_data_entry_record(data_entry_record=updated_entry).to_json()
            client.put_object(
                Body=json_object,
                Bucket=bucket_v2,
                Key=f"{updated_entry.language}/f{str(uuid.uuid4())}"
            )

        return {"statusCode": 200, "body": json.dumps({})}

    return db.with_transaction(update_status)


def get_data_entries(event, context):
    # todo: add json schema validation
    query_object = event['queryStringParameters']

    page_size = int(query_object['page_size'])
    language = query_object['language']
    approval_status = ApprovalStatus[query_object['approval_status']]
    is_ascending = query_object['is_ascending'].lower() == 'true'
    source = query_object['source'] if 'source' in query_object else None
    if 'page_token' in query_object:
        token = query_object['page_token']
        decoded_token = base_64_decode_json(token)
        prev_entry_count = decoded_token['entry_count']
    else:
        decoded_token = token = prev_entry_count = None

    config = ProjectConfig()
    db = DataEntryRecordRecordDB(config)
    entries = db.get_data_entries(language=language, approval_status=approval_status,
                                  prev_entry_count=prev_entry_count, page_size=page_size, is_ascending=is_ascending, source=source)
    has_next = len(entries) == page_size
    response = {
        'data_entries': [DataEntryView.from_data_entry_record(e).to_dict() for e in entries],
        'next_page_token': base_64_encode_json({'entry_count': entries[-1].entry_count}) if has_next else None,
        'previous_page_token': token
    }

    return {"statusCode": 200, "body": json.dumps(response)}


def get_statistics(event, context):
    query_object = event['queryStringParameters']

    language = query_object['language']
    source = query_object['source'] if 'source' in query_object else None

    config = ProjectConfig()
    db = DataEntryRecordRecordDB(config)
    entries = db.get_statistics(language=language, source=source)

    response = {
        'statistics': [e.to_dict() for e in entries]
    }

    return {"statusCode": 200, "body": json.dumps(response)}


def get_data_entry(event, context):
    data_entry_id = uuid.UUID(event['pathParameters']['id'])
    config = ProjectConfig()
    db = DataEntryRecordRecordDB(config)
    existing = db.find_one_by_id(id=data_entry_id)
    if existing is None:
        return {"statusCode": 404, "body": json.dumps({"msg": f"{str(data_entry_id)} is not found"})}
    else:
        return {
            "statusCode": 200,
            "body": json.dumps(DataEntryView.from_data_entry_record(data_entry_record=existing).to_dict())
        }


def base_64_encode_json(json_content: dict) -> str:
    message_bytes = json.dumps(json_content).encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    return base64_bytes.decode('ascii')


def base_64_decode_json(encoded: str) -> dict:
    base64_bytes = encoded.encode('ascii')
    return json.loads(base64.b64decode(base64_bytes))
