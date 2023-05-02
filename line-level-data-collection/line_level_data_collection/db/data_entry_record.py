import copy
import datetime
import json
import uuid
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from functools import partial
from typing import List, Optional, Tuple

import psycopg2.extras
from dataclasses_json import dataclass_json
from psycopg2 import extensions

from line_level_data_collection import time_util
from line_level_data_collection.db.base import PGDatabase

# call it in any place of your program
# before working with UUID objects in PostgreSQL
# https://stackoverflow.com/questions/51105100/psycopg2-cant-adapt-type-uuid
psycopg2.extras.register_uuid()


class ApprovalStatus(Enum):
    UNPROCESSED = 1
    APPROVED = 2
    REJECTED = 3


@dataclass
class DataEntryRecord:
    version: int
    source: str
    id: uuid
    label: str
    label_type: str
    device_id: str
    user_id: str
    strokes: List[dict]  # json
    language: str
    created_at: datetime.datetime
    extra_metadata: dict  # json
    lambda_event: dict
    entry_count: int = None
    approval_status: ApprovalStatus = ApprovalStatus.UNPROCESSED

    def __post_init__(self):
        if self.created_at is not None:
            assert self.created_at.tzinfo == datetime.timezone.utc, "please use datetime with utc timezone"

    def to_tuple(self):
        return (
            self.version,
            self.source,
            self.id,
            self.label,
            self.label_type,
            self.device_id,
            self.user_id,
            json.dumps(self.strokes),
            self.language,
            self.created_at,
            json.dumps(self.extra_metadata),
            json.dumps(self.lambda_event),
            self.approval_status.value,
        )

    @classmethod
    def from_event_json_payload(cls, json_payload, event):
        return DataEntryRecord(
            version=json_payload['version'],
            source=json_payload['source'],
            id=uuid.UUID(json_payload['id']),
            label=json_payload['label']['content'],
            label_type=json_payload['label']['labelType'],
            device_id=json_payload['deviceID'],
            user_id=json_payload['userID'],
            strokes=json_payload['strokes'],
            language=json_payload['language'],
            created_at=time_util.parse_timestamp_iso_string_utc(event['time']),
            extra_metadata={},
            lambda_event=event
        )

    @classmethod
    def from_db_result(cls, db_result: Tuple) -> 'DataEntryRecord':
        result_list = list(db_result)
        result_list[-1] = ApprovalStatus(result_list[-1])
        return DataEntryRecord(*result_list)

    def update(self, update_data: dict):
        new_entry = copy.deepcopy(self)
        if 'label' in update_data:
            new_entry.label = update_data['label']

        if 'approval_status' in update_data:
            new_entry.approval_status = ApprovalStatus[update_data['approval_status']]

        has_changed = new_entry != self

        return new_entry, has_changed

    def content_equal(self, another: 'DataEntryRecord'):
        if another is None:
            return False

        another_copy = copy.deepcopy(another)
        another_copy.entry_count = self.entry_count
        return another_copy == self


@dataclass_json
@dataclass
class DataEntryStatistics:
    language: str
    status: str
    count: int

    @classmethod
    def from_query_result(cls, rows) -> List['DataEntryStatistics']:
        result = []
        for row in rows:
            row: Tuple
            result.append(DataEntryStatistics(language=row[0], status=ApprovalStatus(row[1]).name, count=row[2]))
        return result


@dataclass_json
@dataclass
class DataEntryCount:
    label: str
    status: str
    count: int

    @classmethod
    def from_query_result(cls, rows) -> List['DataEntryCount']:
        result = []
        for row in rows:
            row: Tuple
            result.append(DataEntryCount(label=row[0], status=ApprovalStatus(row[1]).name, count=row[2]))
        return result

    @classmethod
    def to_response_json(cls, entries: List['DataEntryCount']) -> List[dict]:
        result = defaultdict(dict)
        for e in entries:
            label_statistics = result[e.label]
            label_statistics[e.status] = e.count
        result_list = []
        for k, v in result.items():
            v['label'] = k
            v['counts'] = [{'status': status, 'count': count} for status, count in v.items()]
            result_list.append(v)
        return result_list


class DataEntryRecordRecordDB(PGDatabase):
    def __create_record_if_not_exists(self, record: DataEntryRecord, cur) -> bool:
        query = "Select * From data_entry where id=%s limit 1"
        cur.execute(query, (record.id,))
        if cur.fetchone() is None:
            statment = "Insert into data_entry (version,source,id,label,label_type,device_id, user_id," \
                       "strokes,language, created_at, extra_metadata, event, approval_status)" \
                       "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            tp = record.to_tuple()
            cur.execute(statment, tp)
            already_exists = False
        else:
            already_exists = True
        return already_exists

    def create_record_if_not_exists(self, record: DataEntryRecord) -> bool:
        lambda_f = partial(self.__create_record_if_not_exists, record)
        return self.with_transaction(lambda_f)

    def __find_one_by_id(self, id: uuid, cur):
        cur.execute(
            "select version,source,id,label,label_type,device_id, user_id,"
            " strokes,language,created_at, extra_metadata, event, entry_count, approval_status"
            " from data_entry where id=%s limit 1",
            (id,))
        result = cur.fetchone()
        if result is None:
            return None
        else:
            return DataEntryRecord.from_db_result(result)

    def find_one_by_id(self, id: uuid) -> Optional[DataEntryRecord]:
        lambda_f = partial(self.__find_one_by_id, id)
        return self.with_transaction(lambda_f)

    def __count(self, cur):
        cur.execute("select count(*) from data_entry")
        return cur.fetchone()[0]

    def count(self) -> int:
        return self.with_transaction(self.__count)

    def __get_languages(self, cur: extensions.cursor):
        cur.execute("select distinct(language) from data_entry")
        result = cur.fetchall()
        if result is None:
            return []
        else:
            return [r[0] for r in result]

    def get_languages(self) -> List[str]:
        return self.with_transaction(self.__get_languages)

    def update_data_entry(self, new_data_entry: DataEntryRecord, cursor: extensions.cursor) -> int:
        statement = "update data_entry set version=%s,source=%s, label=%s,label_type=%s," \
                    "device_id=%s, user_id=%s, strokes=%s,language=%s, created_at=%s, extra_metadata=%s," \
                    "event=%s, approval_status=%s where id=%s"
        fields = list(new_data_entry.to_tuple())
        tp = tuple(fields[:2] + fields[3:] + [fields[2]])
        cursor.execute(statement, tp)
        updated_rows = cursor.rowcount
        return updated_rows

    def get_data_entries(self, language: str, approval_status: ApprovalStatus, prev_entry_count: Optional[int] = None,
                         page_size: int = 20, is_ascending: bool = True, source: Optional[str] = None) -> List[
        DataEntryRecord]:
        return self.with_transaction(
            lambda cursor: self.__get_data_entries(cursor=cursor, language=language, approval_status=approval_status,
                                                   prev_entry_count=prev_entry_count, page_size=page_size,
                                                   is_ascending=is_ascending, source=source))

    def __get_data_entries(self, cursor: extensions.cursor, language: str, approval_status: ApprovalStatus,
                           prev_entry_count: Optional[int], page_size: int, is_ascending: bool,
                           source: Optional[str] = None) \
            -> List[DataEntryRecord]:
        stmt_select = 'SELECT version,source,id,label,label_type,device_id, user_id,strokes,language,created_at, extra_metadata, event, entry_count, approval_status'
        stmt_from = 'FROM data_entry'
        stmt_where = 'WHERE language = %s AND approval_status = %s'
        query_params = [language, approval_status.value]
        if prev_entry_count is not None:
            if is_ascending:
                stmt_where += ' AND entry_count > %s'
            else:
                stmt_where += ' AND entry_count < %s'
            query_params.append(prev_entry_count)
        if source is not None:
            stmt_where += ' AND source = %s'
            query_params.append(source)
        stmt_order_by = 'ORDER BY entry_count'
        stmt_sort = '' if is_ascending else 'DESC'
        stmt_limit = 'LIMIT %s'
        query_params.append(page_size)

        statement = f'{stmt_select} {stmt_from} {stmt_where} {stmt_order_by} {stmt_sort} {stmt_limit}'
        cursor.execute(statement, tuple(query_params))
        result = cursor.fetchall()
        return [DataEntryRecord.from_db_result(e) for e in result]

    def get_statistics(self, language: str, source: Optional[str] = None) -> List[DataEntryStatistics]:
        return self.with_transaction(
            lambda cursor: self.__get_statistics(cursor=cursor, language=language, source=source))

    def __get_statistics(self, cursor: extensions.cursor, language: str, source: Optional[str] = None) -> List[
        DataEntryStatistics]:
        stmt_before_where = 'SELECT language, approval_status, count(approval_status) as count FROM data_entry'
        stmt_where = 'WHERE language = %s'
        query_params = [language]
        if source is not None:
            stmt_where += ' AND source LIKE %s'
            query_params.append(source)
        stmt_after_where = 'GROUP BY language, approval_status ORDER BY approval_status'
        statement = f'{stmt_before_where} {stmt_where} {stmt_after_where}'
        cursor.execute(statement, tuple(query_params))
        result = cursor.fetchall()
        return DataEntryStatistics.from_query_result(result)

    def get_sources(self, language: str) -> List[str]:
        return self.with_transaction(
            lambda cursor: self.__get_sources(cursor=cursor, language=language))

    def __get_sources(self, cursor: extensions.cursor, language: str) -> List[str]:
        statement = "SELECT DISTINCT(source) FROM data_entry WHERE language = %s"
        query_params = [language]
        cursor.execute(statement, tuple(query_params))
        result = cursor.fetchall()
        if result is None:
            return []
        else:
            return [r[0] for r in result]

    def count_labels(self, labels: List[str], language: str) -> List[DataEntryCount]:
        return self.with_transaction(
            lambda cursor: self.__count_labels(cursor=cursor, language=language, labels=labels))

    def __count_labels(self, cursor: extensions.cursor, language: str, labels) -> List[DataEntryCount]:
        labels = tuple(labels)
        statement = "SELECT label, approval_status, count(*) FROM data_entry " \
                    "WHERE language = %s and label in %s group by label, approval_status " \
                    "order by label asc, approval_status asc"
        query_params = [language, labels]
        cursor.execute(statement, tuple(query_params))
        result = cursor.fetchall()
        if result is None:
            return []
        else:
            return DataEntryCount.from_query_result(result)
