from line_level_data_collection.db.base import PGDatabase


class DatabaseTestingHelper(PGDatabase):
    def clean_db(self, table_name: str):
        conn = self.connect()
        cur = conn.cursor()
        # https://dba.stackexchange.com/questions/308316/how-do-you-reset-a-serial-type-back-to-0-after-deleting-all-rows-in-a-table
        # noinspection SqlWithoutWhere
        cur.execute(f"truncate table {table_name} restart identity")
        conn.commit()
        cur.close()
        conn.close()
