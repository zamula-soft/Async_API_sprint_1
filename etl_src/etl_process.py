from loguru import logger
import time
from contextlib import closing

from etl_src.extract.extractor import PostgresExtractor
from etl_src.transform.transformer import DataTransform
from etl_src.load.loader import Service

PG_BATCH_SIZE = 20
TF_BATCH_SIZE = 5
ES_BATCH_SIZE = 5


def etl_process():
    pg_extractor = PostgresExtractor()
    data_transformer = DataTransform()
    es_loader = Service()
    with closing(pg_extractor.pg_conn) as pg_conn:
        raw_generator = pg_extractor.get_batches(PG_BATCH_SIZE)
        for raw_data in raw_generator:
            transformed_data = data_transformer.transform_data(raw_data, TF_BATCH_SIZE)
            logger.debug(transformed_data)
            for ts_data in transformed_data:
                logger.debug(ts_data)
                es_loader.load_data(ts_data, ES_BATCH_SIZE)
        pg_conn.commit()
        pg_conn.close()


if __name__ == '__main__':
    while True:
        etl_process()
        time.sleep(5)
