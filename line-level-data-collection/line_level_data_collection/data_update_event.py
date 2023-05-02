import copy
import typing
import uuid
from dataclasses import dataclass
from typing import List, Any

from dataclasses_json import dataclass_json

from line_level_data_collection.db.data_entry_record import DataEntryRecord
from line_level_data_collection.time_util import *


@dataclass_json
@dataclass
class DataEntryUpdateEvent:
    source: str
    id: str
    label: str
    label_type: str
    device_id: str
    user_id: str
    strokes: List[Any]
    language: str
    event_created_time_epoch_seconds: float
    approval_status: str

    @classmethod
    def from_data_entry_record(cls, data_entry_record: DataEntryRecord) -> 'DataEntryUpdateEvent':
        return DataEntryUpdateEvent(
            source=data_entry_record.source,
            id=str(data_entry_record.id),
            label=str(data_entry_record.label),
            label_type=data_entry_record.label_type,
            user_id=data_entry_record.user_id,
            device_id=data_entry_record.device_id,
            strokes=data_entry_record.strokes,
            language=data_entry_record.language,
            event_created_time_epoch_seconds=utc_datetime_now().timestamp(),
            approval_status=data_entry_record.approval_status.name
        )

    def content_equal(self, another: 'DataEntryUpdateEvent') -> bool:
        if another is None:
            return False
        another_copy = copy.deepcopy(another)
        another_copy.event_created_time_epoch_seconds = self.event_created_time_epoch_seconds
        return another_copy == self


@dataclass_json
@dataclass
class DataEntryUpdateEventV2:
    source: str
    data_entry_id: str
    label: str
    label_type: str
    device_id: str
    user_id: str
    strokes: List[Any]
    language: str
    event_created_time: str
    approval_status: str
    id: str

    @classmethod
    def from_data_entry_record(cls, data_entry_record: DataEntryRecord) -> 'DataEntryUpdateEventV2':
        return DataEntryUpdateEventV2(
            source=data_entry_record.source,
            data_entry_id=str(data_entry_record.id),
            label=str(data_entry_record.label),
            label_type=data_entry_record.label_type,
            user_id=data_entry_record.user_id,
            device_id=data_entry_record.device_id,
            strokes=data_entry_record.strokes,
            language=data_entry_record.language,
            event_created_time=utc_timestamp_to_iso_string(utc_datetime_now()),
            approval_status=data_entry_record.approval_status.name,
            id=str(uuid.uuid4())
        )

    def content_equal(self, another: 'DataEntryUpdateEventV2') -> bool:
        if another is None:
            return False
        another_copy = copy.deepcopy(another)
        another_copy.event_created_time = self.event_created_time
        another_copy.id = self.id
        return another_copy == self

    def to_tuple(self) -> typing.Tuple[str, str, typing.Any, str]:
        return self.to_json(), self.language, parse_timestamp_iso_string_utc(
            self.event_created_time), self.id
