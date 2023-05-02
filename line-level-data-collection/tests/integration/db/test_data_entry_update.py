import os

from line_level_data_collection.config import ProjectConfig
from line_level_data_collection.db.data_entry_update_record import DataEntryUpdateRecordRecordDB
from line_level_data_collection.test_util import generate_update_record
from line_level_data_collection.test_util.testdb import DatabaseTestingHelper
from line_level_data_collection.time_util import utc_datetime_now


def setup_function(fun):
    os.environ['CAPACITY'] = '100'
    print("in setup function: " + fun.__name__)
    DatabaseTestingHelper(config=ProjectConfig("integration-test")).clean_db("data_entry_update")


def teardown_function(function):
    del os.environ['CAPACITY']
    print(f"teardown function for {function.__name__}")
    DatabaseTestingHelper(config=ProjectConfig("integration-test")).clean_db("data_entry_update")


def test_db_append_record():
    db = DataEntryUpdateRecordRecordDB(config=ProjectConfig("integration-test"))
    assert db.count() == 0
    ts = utc_datetime_now()
    record = generate_update_record()
    db.append_record(record)
    assert db.count() == 1


def test_db_count_by_language():
    db = DataEntryUpdateRecordRecordDB(config=ProjectConfig("integration-test"))
    assert db.count() == 0
    ts = utc_datetime_now()
    record = generate_update_record(language='lang1')
    db.append_record(record)
    record = generate_update_record(language='lang2')
    db.append_record(record)
    assert db.count(language='lang2') == 1


def test_db_read_one_record():
    db = DataEntryUpdateRecordRecordDB(config=ProjectConfig("integration-test"))
    record = generate_update_record()
    db.append_record(record)
    retrieved_records = db.get(language=record.language, limit=100)
    assert retrieved_records[0] == record


def test_db_read_multiple_records():
    db = DataEntryUpdateRecordRecordDB(config=ProjectConfig("integration-test"))
    test_lang = 'aloha'
    records = [generate_update_record(language=test_lang) for _ in range(10)]
    for r in records:
        db.append_record(r)
    assert db.count(language=test_lang) == 10
    retrieved_records = db.get(language=test_lang, limit=100)
    assert retrieved_records == records


def test_db_remove_records():
    db = DataEntryUpdateRecordRecordDB(config=ProjectConfig("integration-test"))
    test_lang = 'test_lang'
    records = [generate_update_record(language=test_lang) for _ in range(10)]
    for r in records:
        db.append_record(r)
    db.remove(events=records)
    assert db.count() == 0
