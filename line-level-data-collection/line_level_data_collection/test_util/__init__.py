import uuid

from line_level_data_collection.data_update_event import DataEntryUpdateEventV2
from line_level_data_collection.db.data_entry_record import ApprovalStatus, DataEntryRecord
from line_level_data_collection.time_util import utc_datetime_now, utc_timestamp_to_iso_string


class FakeContext:
    function_name = "some_name"
    function_version = "$LATEST"


def generate_entry_record(
        id=None,
        version=1,
        source="source",
        label_type="LATEX",
        label='label',
        device_id='aldskfj',
        user_id='alsdkfj',
        strokes=None,
        language='lang1',
        created_at=None,
        extra_metadata=None,
        approval_status=ApprovalStatus.APPROVED,
        lambda_event=None
) -> DataEntryRecord:
    if created_at is None:
        created_at = utc_datetime_now()
    if id is None:
        id = uuid.uuid4()
    if strokes is None:
        strokes = [
            {
                "points": [
                    {
                        "x": 113.263427734375,
                        "y": 279.76385498046875,
                        "delay": 16
                    }
                ],
                "startTimestamp": 1676453403551
            }
        ]
    if extra_metadata is None:
        extra_metadata = {"foo": 'bar'}
    if lambda_event is None:
        lambda_event = {"some_event": "event"}
    return DataEntryRecord(
        id=id,
        version=version,
        source=source,
        label_type=label_type,
        label=label,
        device_id=device_id,
        user_id=user_id,
        strokes=strokes,
        language=language,
        created_at=created_at,
        extra_metadata=extra_metadata,
        approval_status=approval_status,
        lambda_event=lambda_event
    )


def generate_update_record(
        id=None,
        version=1,
        source="source",
        label_type="LATEX",
        label='label',
        device_id='aldskfj',
        user_id='alsdkfj',
        strokes=None,
        language='lang1',
        created_at=None,
        extra_metadata=None,
        approval_status=ApprovalStatus.APPROVED,
        lambda_event=None,
        update_event_id=None
) -> DataEntryUpdateEventV2:
    if created_at is None:
        created_at = utc_datetime_now()

    if id is None:
        id = uuid.uuid4()

    if strokes is None:
        strokes = [
            {
                "points": [
                    {
                        "x": 113.263427734375,
                        "y": 279.76385498046875,
                        "delay": 16
                    }
                ],
                "startTimestamp": 1676453403551
            }
        ]
    if extra_metadata is None:
        extra_metadata = {"foo": 'bar'}
    if lambda_event is None:
        lambda_event = {"some_event": "event"}
    if update_event_id is None:
        update_event_id = str(uuid.uuid4())
    return DataEntryUpdateEventV2(
        source=source,
        data_entry_id=str(id),
        label=label,
        label_type=label_type,
        user_id=user_id,
        device_id=device_id,
        strokes=strokes,
        language=language,
        event_created_time=utc_timestamp_to_iso_string(created_at),
        approval_status=approval_status.name,
        id=update_event_id
    )
