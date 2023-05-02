import typing
from dataclasses import dataclass

from dataclasses_json import dataclass_json

from line_level_data_collection import time_util
from line_level_data_collection.db.data_entry_record import DataEntryRecord


@dataclass_json
@dataclass
class DataEntryView:
    source: str
    id: str
    label: str
    label_type: str
    device_id: str
    user_id: str
    strokes: typing.Any  # json
    language: str
    created_at: str
    approval_status: str

    @classmethod
    def from_data_entry_record(cls, data_entry_record: DataEntryRecord) -> 'DataEntryView':
        return DataEntryView(
            source=data_entry_record.source,
            id=str(data_entry_record.id),
            label=str(data_entry_record.label),
            label_type=data_entry_record.label_type,
            user_id=data_entry_record.user_id,
            device_id=data_entry_record.device_id,
            strokes=data_entry_record.strokes,
            language=data_entry_record.language,
            created_at=time_util.utc_timestamp_to_iso_string(data_entry_record.created_at),
            approval_status=data_entry_record.approval_status.name
        )
