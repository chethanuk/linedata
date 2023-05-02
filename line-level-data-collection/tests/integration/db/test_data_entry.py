import copy
import uuid

from line_level_data_collection.config import ProjectConfig
from line_level_data_collection.db.data_entry_record import DataEntryRecordRecordDB, DataEntryRecord, ApprovalStatus, \
    DataEntryStatistics, DataEntryCount
from line_level_data_collection.test_util import generate_entry_record
from line_level_data_collection.test_util.testdb import DatabaseTestingHelper
from line_level_data_collection.time_util import utc_datetime_now


def setup_function(fun):
    print("in setup function: " + fun.__name__)
    DatabaseTestingHelper(config=ProjectConfig("integration-test")).clean_db("data_entry")


def teardown_function(function):
    print(f"teardown function for {function.__name__}")
    DatabaseTestingHelper(config=ProjectConfig("integration-test")).clean_db("data_entry")


def test_db_insert_if_not_exists():
    db = DataEntryRecordRecordDB(config=ProjectConfig("integration-test"))
    assert db.count() == 0
    ts = utc_datetime_now()
    record = DataEntryRecord(
        id=uuid.uuid4(),
        version=1,
        source="source",
        label_type="LATEX",
        label='label',
        device_id='aldskfj',
        user_id='alsdkfj',
        strokes=[{"hello": 'world'}],
        language='lang',
        created_at=ts,
        extra_metadata={"foo": 'bar'},
        approval_status=ApprovalStatus.APPROVED,
        lambda_event={"some_event": "event"}
    )
    assert db.create_record_if_not_exists(record) is False
    assert db.count() == 1
    assert db.create_record_if_not_exists(record) is True
    assert db.count() == 1


def test_db_insert_insert_and_retrieve():
    db = DataEntryRecordRecordDB(config=ProjectConfig("integration-test"))
    assert db.count() == 0
    ts = utc_datetime_now()
    record = DataEntryRecord(
        id=uuid.uuid4(),
        version=1,
        source="source",
        label_type="LATEX",
        label='label',
        device_id='aldskfj',
        user_id='alsdkfj',
        strokes=[{"hello": 'world'}],
        language='lang',
        created_at=ts,
        extra_metadata={"foo": 'bar'},
        approval_status=ApprovalStatus.APPROVED,
        lambda_event={"some_event": "event"}
    )
    assert db.create_record_if_not_exists(record) is False
    assert db.count() == 1
    retrieved = db.find_one_by_id(record.id)
    assert retrieved.entry_count == 1
    assert record.content_equal(retrieved)


def test_db_get_all_languages():
    db = DataEntryRecordRecordDB(config=ProjectConfig("integration-test"))
    assert db.count() == 0
    ts = utc_datetime_now()
    record0 = generate_entry_record(language="lang1")
    record1 = generate_entry_record(language="lang1")
    record2 = generate_entry_record(language="lang2")
    assert db.create_record_if_not_exists(record0) is False
    assert db.create_record_if_not_exists(record1) is False
    assert db.create_record_if_not_exists(record2) is False
    assert db.count() == 3
    assert set(db.get_languages()) == {'lang1', 'lang2'}


def test_db_update_data_entry_label_and_status():
    db = DataEntryRecordRecordDB(config=ProjectConfig("integration-test"))
    assert db.count() == 0
    record0 = generate_entry_record(language="lang1", approval_status=ApprovalStatus.UNPROCESSED)
    assert db.create_record_if_not_exists(record0) is False

    record_new = copy.deepcopy(record0)
    record_new.label = 'new_label'
    record_new.approval_status = ApprovalStatus.REJECTED
    updated_row_count = db.with_transaction(
        lambda cursor: db.update_data_entry(new_data_entry=record_new, cursor=cursor))

    assert db.find_one_by_id(record0.id).content_equal(record_new)
    assert updated_row_count == 1


def test_get_entries_default():
    db = DataEntryRecordRecordDB(config=ProjectConfig("integration-test"))
    assert db.count() == 0
    records = [generate_entry_record(language='math', approval_status=ApprovalStatus.APPROVED) for _ in range(3)]
    for r in records:
        assert db.create_record_if_not_exists(r) is False
        assert db.create_record_if_not_exists(
            generate_entry_record(language='random', approval_status=ApprovalStatus.APPROVED)) is False
        assert db.create_record_if_not_exists(
            generate_entry_record(language='math', approval_status=ApprovalStatus.REJECTED)) is False

    entries = db.get_data_entries(language='math', approval_status=ApprovalStatus.APPROVED, prev_entry_count=None,
                                  page_size=2)
    assert len(entries) == 2

    expected = records[:2]
    for i in range(2):
        assert expected[i].content_equal(entries[i])


def test_get_entries_with_entry_count():
    db = DataEntryRecordRecordDB(config=ProjectConfig("integration-test"))
    assert db.count() == 0
    records = [generate_entry_record(language='math', approval_status=ApprovalStatus.APPROVED) for _ in range(3)]
    for r in records:
        assert db.create_record_if_not_exists(r) is False
        assert db.create_record_if_not_exists(
            generate_entry_record(language='random', approval_status=ApprovalStatus.APPROVED)) is False
        assert db.create_record_if_not_exists(
            generate_entry_record(language='math', approval_status=ApprovalStatus.REJECTED)) is False

    entries = db.get_data_entries(language='math', approval_status=ApprovalStatus.APPROVED, prev_entry_count=1,
                                  page_size=2)
    assert len(entries) == 2
    expected = records[1:]
    for i in range(2):
        assert expected[i].content_equal(entries[i])


def test_get_statistics():
    db = DataEntryRecordRecordDB(config=ProjectConfig("integration-test"))
    assert db.count() == 0

    db.create_record_if_not_exists(generate_entry_record(language='lang', approval_status=ApprovalStatus.REJECTED))
    db.create_record_if_not_exists(generate_entry_record(language='lang', approval_status=ApprovalStatus.REJECTED))
    db.create_record_if_not_exists(generate_entry_record(language='lang', approval_status=ApprovalStatus.REJECTED))
    db.create_record_if_not_exists(generate_entry_record(language='lang', approval_status=ApprovalStatus.APPROVED))
    db.create_record_if_not_exists(generate_entry_record(language='lang', approval_status=ApprovalStatus.APPROVED))
    db.create_record_if_not_exists(generate_entry_record(language='lang', approval_status=ApprovalStatus.UNPROCESSED))
    db.create_record_if_not_exists(generate_entry_record(language='lang2', approval_status=ApprovalStatus.UNPROCESSED))

    result = db.get_statistics(language='lang')
    assert len(result) == 3
    expected = [
        DataEntryStatistics(language='lang', status=ApprovalStatus.UNPROCESSED.name, count=1),
        DataEntryStatistics(language='lang', status=ApprovalStatus.APPROVED.name, count=2),
        DataEntryStatistics(language='lang', status=ApprovalStatus.REJECTED.name, count=3)
    ]
    assert result == expected


def test_get_sources():
    db = DataEntryRecordRecordDB(config=ProjectConfig("integration-test"))
    assert db.count() == 0

    db.create_record_if_not_exists(
        generate_entry_record(language='lang', approval_status=ApprovalStatus.REJECTED, source='david'))
    db.create_record_if_not_exists(
        generate_entry_record(language='lang', approval_status=ApprovalStatus.REJECTED, source='david'))
    db.create_record_if_not_exists(
        generate_entry_record(language='lang', approval_status=ApprovalStatus.REJECTED, source='david'))
    db.create_record_if_not_exists(
        generate_entry_record(language='lang', approval_status=ApprovalStatus.APPROVED, source='david'))
    db.create_record_if_not_exists(
        generate_entry_record(language='lang', approval_status=ApprovalStatus.APPROVED, source='paco'))
    db.create_record_if_not_exists(
        generate_entry_record(language='lang', approval_status=ApprovalStatus.UNPROCESSED, source='paco'))
    db.create_record_if_not_exists(
        generate_entry_record(language='lang2', approval_status=ApprovalStatus.UNPROCESSED, source='felix'))

    result = db.get_sources(language='lang')
    assert set(result) == {'david', 'paco'}


def test_get_label_count():
    db = DataEntryRecordRecordDB(config=ProjectConfig("integration-test"))
    assert db.count() == 0

    db.create_record_if_not_exists(
        generate_entry_record(language='lang', approval_status=ApprovalStatus.REJECTED, label='bar'))
    db.create_record_if_not_exists(
        generate_entry_record(language='lang', approval_status=ApprovalStatus.REJECTED, label='foo'))
    db.create_record_if_not_exists(
        generate_entry_record(language='lang', approval_status=ApprovalStatus.UNPROCESSED, label='foo'))
    db.create_record_if_not_exists(
        generate_entry_record(language='lang', approval_status=ApprovalStatus.APPROVED, label='foo'))

    result = db.count_labels(language='lang', labels=['bar', 'foo'])
    assert result == [
        DataEntryCount(label='bar', status=ApprovalStatus.REJECTED.name, count=1),
        DataEntryCount(label='foo', status=ApprovalStatus.UNPROCESSED.name, count=1),
        DataEntryCount(label='foo', status=ApprovalStatus.APPROVED.name, count=1),
        DataEntryCount(label='foo', status=ApprovalStatus.REJECTED.name, count=1),
    ]
