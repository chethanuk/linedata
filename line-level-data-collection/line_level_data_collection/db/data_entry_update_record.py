from functools import partial
from typing import List, Optional

from line_level_data_collection.data_update_event import DataEntryUpdateEventV2
from line_level_data_collection.db.base import PGDatabase


class DataEntryUpdateRecordRecordDB(PGDatabase):
    def _count(self, language: Optional[str], cur) -> int:
        if language is None:
            cur.execute("select count(*) from data_entry_update")
        else:
            # may need index
            cur.execute("select count(*) from data_entry_update where language=%s", (language,))
        return cur.fetchone()[0]

    def count(self, language: Optional[str] = None) -> int:
        lambda_f = partial(self._count, language)
        return self.with_transaction(lambda_f)

    def get(self, language: str, limit: int) -> List[DataEntryUpdateEventV2]:
        lambda_f = partial(self._get, language, limit)
        return self.with_transaction(lambda_f)

    def _get(self, language: str, limit: int, cur):
        query = "Select event_content from data_entry_update where language=%s order by created_at limit %s"
        cur.execute(query, (language, limit))
        result = cur.fetchall()
        return [DataEntryUpdateEventV2.from_dict(e[0]) for e in result]

    def remove(self, events: List[DataEntryUpdateEventV2]) -> None:
        lambda_f = partial(self._remove, events)
        return self.with_transaction(lambda_f)

    def _remove(self, events: List[DataEntryUpdateEventV2], cur) -> None:
        statement = "delete from data_entry_update where id in %s"
        ids = tuple([e.id for e in events])
        cur.execute(statement, (ids,))

    # noinspection PyMethodMayBeStatic
    def _append_record(self, record: DataEntryUpdateEventV2, cur) -> None:
        statement = "Insert into data_entry_update (event_content,language,created_at, id)" \
                    "VALUES (%s, %s, %s, %s)"
        tp = record.to_tuple()
        cur.execute(statement, tp)

    def append_record(self, record: DataEntryUpdateEventV2) -> bool:
        lambda_f = partial(self._append_record, record)
        return self.with_transaction(lambda_f)
