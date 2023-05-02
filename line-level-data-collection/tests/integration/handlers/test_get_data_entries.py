import json

from line_level_data_collection.config import ProjectConfig, project_root
from line_level_data_collection.data_entry_view import DataEntryView
from line_level_data_collection.db.data_entry_record import DataEntryRecordRecordDB, ApprovalStatus
from line_level_data_collection.handlers.verification import get_data_entries, base_64_decode_json, base_64_encode_json
from line_level_data_collection.test_util import FakeContext, generate_entry_record
from line_level_data_collection.test_util.testdb import DatabaseTestingHelper


def setup_function(fun):
    print("in setup function: " + fun.__name__)
    # clean db
    tables = [
        "data_entry"
    ]
    for table in tables:
        DatabaseTestingHelper(ProjectConfig("test")).clean_db(table_name=table)


def teardown_function(function):
    print(f"teardown function for {function.__name__}")
    # clean db
    tables = [
        "data_entry"
    ]
    for table in tables:
        DatabaseTestingHelper(ProjectConfig("test")).clean_db(table_name=table)


def test_lambda_handler():
    db = DataEntryRecordRecordDB(ProjectConfig("test"))
    records = [generate_entry_record(language="math", approval_status=ApprovalStatus.UNPROCESSED, device_id=f'{i}') for
               i in range(11)]
    for r in records:
        db.create_record_if_not_exists(record=r)

    event_path = project_root / "tests/resources/get_data_entries.json"
    with event_path.open(mode="r") as f:
        event = json.loads(f.read())
    event['queryStringParameters']['is_ascending'] = 'true'

    result = get_data_entries(event=event, context=FakeContext())
    response_json = json.loads(result['body'])
    assert response_json['data_entries'] == [DataEntryView.from_data_entry_record(r).to_dict() for r in records[:10]]
    assert response_json['previous_page_token'] is None
    assert base_64_decode_json(response_json['next_page_token']) == {'entry_count': 10}


def test_lambda_handler_with_count():
    db = DataEntryRecordRecordDB(ProjectConfig("test"))
    records = [generate_entry_record(language="math", approval_status=ApprovalStatus.UNPROCESSED) for i in range(11)]
    for r in records:
        db.create_record_if_not_exists(record=r)

    event_path = project_root / "tests/resources/get_data_entries.json"
    token = base_64_encode_json({'entry_count': 1})
    with event_path.open(mode="r") as f:
        event = json.loads(f.read())
    event['queryStringParameters']['page_token'] = token
    event['queryStringParameters']['page_size'] = 3
    event['queryStringParameters']['is_ascending'] = 'true'

    result = get_data_entries(event=event, context=FakeContext())
    response_json = json.loads(result['body'])
    assert response_json['data_entries'] == [DataEntryView.from_data_entry_record(r).to_dict() for r in records[1:4]]
    assert response_json['previous_page_token'] == token
    assert base_64_decode_json(response_json['next_page_token']) == {'entry_count': 4}


def test_lambda_handler_desc():
    db = DataEntryRecordRecordDB(ProjectConfig("test"))
    records = [generate_entry_record(language="math", approval_status=ApprovalStatus.UNPROCESSED, device_id=f'{i}') for
               i in range(11)]
    for r in records:
        db.create_record_if_not_exists(record=r)

    event_path = project_root / "tests/resources/get_data_entries.json"
    # token = base_64_encode_json({'entry_count': 11})
    with event_path.open(mode="r") as f:
        event = json.loads(f.read())
    # event['queryStringParameters']['page_token'] = token
    event['queryStringParameters']['page_size'] = 3
    event['queryStringParameters']['is_ascending'] = 'false'

    result = get_data_entries(event=event, context=FakeContext())
    response_json = json.loads(result['body'])
    assert response_json['data_entries'] == [DataEntryView.from_data_entry_record(r).to_dict() for r in
                                             reversed(records[8:11])]
    assert response_json['previous_page_token'] == None
    assert base_64_decode_json(response_json['next_page_token']) == {'entry_count': 9}


def test_lambda_handler_desc_with_count():
    db = DataEntryRecordRecordDB(ProjectConfig("test"))
    records = [generate_entry_record(language="math", approval_status=ApprovalStatus.UNPROCESSED, device_id=f'{i}') for
               i in range(11)]
    for r in records:
        db.create_record_if_not_exists(record=r)

    event_path = project_root / "tests/resources/get_data_entries.json"
    token = base_64_encode_json({'entry_count': 11})
    with event_path.open(mode="r") as f:
        event = json.loads(f.read())
    event['queryStringParameters']['page_token'] = token
    event['queryStringParameters']['page_size'] = 1
    event['queryStringParameters']['is_ascending'] = 'false'

    result = get_data_entries(event=event, context=FakeContext())
    response_json = json.loads(result['body'])
    assert response_json['data_entries'] == [DataEntryView.from_data_entry_record(r).to_dict() for r in
                                             reversed(records[9:10])]
    assert response_json['previous_page_token'] == token
    assert base_64_decode_json(response_json['next_page_token']) == {'entry_count': 10}
