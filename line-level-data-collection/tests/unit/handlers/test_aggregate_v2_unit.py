from line_level_data_collection.handlers.aggregate_v2 import DataEntryUpdateEventV2Bundle
from line_level_data_collection.test_util import generate_update_record


def test_event_bundle_not_full():
    bundle = DataEntryUpdateEventV2Bundle(
        language='lang',
        events=[generate_update_record() for _ in range(3)],
        capacity=5
    )
    assert bundle.file_name() == 'latest.json'
    assert bundle.remaining_capacity() == 2


def test_event_bundle_full():
    bundle = DataEntryUpdateEventV2Bundle(
        language='lang',
        events=[generate_update_record() for _ in range(3)],
        capacity=3
    )
    assert not bundle.file_name() == 'latest.json'
    assert bundle.remaining_capacity() == 0


def test_event_bundle_add_data():
    bundle = DataEntryUpdateEventV2Bundle(
        language='lang',
        events=[generate_update_record() for _ in range(3)],
        capacity=10
    )
    new_bundle = bundle.add_new_data([generate_update_record()])
    assert new_bundle.remaining_capacity() == 10 - 3 - 1
