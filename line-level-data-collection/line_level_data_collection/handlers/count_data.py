import base64
import json

from line_level_data_collection.config import ProjectConfig
from line_level_data_collection.db.data_entry_record import DataEntryRecordRecordDB, DataEntryCount

from urllib.parse import unquote, quote


def get_data_entry_count(event, context):
    query_object = event['queryStringParameters']
    encoded_label = query_object['encoded_label']
    language = query_object['language']
    decoded_label = url_b64_decode_str(encoded_label)

    config = ProjectConfig()
    db = DataEntryRecordRecordDB(config)
    count_items = db.count_labels(language=language, labels=[decoded_label])
    if len(count_items) == 0:
        return {"statusCode": 404, "body": json.dumps({"msg": f"{str(decoded_label)} is not found"})}
    else:
        entries = DataEntryCount.to_response_json(entries=count_items)
        return {
            "statusCode": 200,
            "body": json.dumps({"entries": entries})
        }


def url_b64_encode_str(label: str) -> str:
    return quote(base64.b64encode(label.encode('utf-8')).decode('utf-8'))


def url_b64_decode_str(encoded: str) -> str:
    return base64.b64decode(unquote(encoded).encode('utf-8')).decode('utf-8')
