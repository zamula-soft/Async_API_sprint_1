from loguru import logger
from contextlib import closing
import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor

from postgres_to_es.config.settings import Settings
from postgres_to_es.state.state import State, JsonFileStorage

PG_SQL_GENRES = """SELECT
   g.id,
   g.name
FROM content.genre g;
"""
PG_SQL_PERSONS = """SELECT
   p.id,
   p.full_name
FROM ccontent.person p;
"""


def connect(settings):
    dbname = settings.psql_dbname
    user = settings.psql_user
    password = settings.psql_password
    host = settings.psql_host
    port = settings.psql_port
    dsl = {'dbname': dbname, 'user': user, 'password': password, 'host': host, 'port': int(port)}
    logger.debug('Connected to PostgresQL Database')
    return psycopg2.connect(**dsl, cursor_factory=DictCursor)


class PostgresExtractor:
    def __init__(self):
        settings = Settings()
        pg_conn = connect(settings)
        self.pg_conn = pg_conn
        self.file_path = settings.file_path

    def get_state(self):
        js_storage = JsonFileStorage(self.file_path)
        state = State(js_storage)
        str_state = {'state': state.get_state('modified')}
        return str_state

    def get_batches_genres(self, batch_size):
        with self.cursor as cursor:
            stmt = sql.SQL(PG_SQL_GENRES)
            cursor.execute(stmt, self.get_state())
            while True:
                records = cursor.fetchmany(batch_size)
                if not records:
                    break
                yield list(records)

    def get_batches_persons(self, batch_size):
        with self.cursor as cursor:
            stmt = sql.SQL(PG_SQL_PERSONS)
            cursor.execute(stmt, self.get_state())
            while True:
                records = cursor.fetchmany(batch_size)
                if not records:
                    break
                yield list(records)
