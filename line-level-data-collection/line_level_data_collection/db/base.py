import hashlib
from typing import Callable, Any, List

import psycopg2

from line_level_data_collection.config import ProjectConfig
from line_level_data_collection.log import LOGGER


def calculate_hash_of_strings(strings: List[str]) -> str:
    digest = hashlib.sha256()
    for string in strings:
        assert isinstance(string, str), type(string)
        digest.update(string.encode(encoding="utf-8"))
    return digest.digest().hex()


class PGDatabase:
    def __init__(
            self,
            config: ProjectConfig
    ):
        config = config.get_config()
        self.dbname = config['database']['database_name']
        self.user = config['database']['username']
        self.password = config['database']['password']
        self.host = config['database']['host']
        self.port = config['database']['port']
        self.conn = None

    def connect(self):
        """Connect to a Postgres database."""
        conn = psycopg2.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            port=self.port,
            dbname=self.dbname
        )
        return conn

    def with_transaction(self, lambda_f: Callable) -> Any:
        conn = None
        try:
            # When a connection exits the with block, if no exception has been raised by the block,
            # the transaction is committed. In case of exception the transaction is rolled back.
            # https://www.psycopg.org/docs/usage.html#transactions-control
            # always commit the transaction
            # https://stackoverflow.com/questions/309834/should-i-commit-or-rollback-a-read-transaction
            # Read Committed is the default isolation level
            conn = self.connect()
            with conn:
                with conn.cursor() as cur:
                    return lambda_f(cur)
        except psycopg2.DatabaseError as e:
            LOGGER.error(e)
            raise e
        finally:
            if conn is not None:
                conn.close()
