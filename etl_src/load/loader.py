from functools import lru_cache

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import streaming_bulk
from fastapi import Depends
from loguru import logger

from etl_src.backoff.backoff import backoff
from src.db.elastic import get_elastic
from src.db.redis import get_redis


class Service:
    """
    Class to load data into Elasticsearch, to create and update indices
    """

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    def load_data(self, transformed_data, chunk_size, index_name):
        if not self.elastic.indices.exists(index=index_name):
            create_index(self.elastic, index_name)
        streaming_bulk(self.elastic, 'update', transformed_data, chunk_size, ignore=400, raise_on_error=True)
        try:
            bulks_processed = 0
            not_ok = []
            streaming_bulk(self.elastic, 'update', transformed_data, chunk_size, raise_on_error=False)

            for cnt, response in enumerate(streaming_bulk(self.elastic, transformed_data, chunk_size)):
                ok, result = response
                if not ok:
                    not_ok.append(result)
                if cnt % chunk_size == 0:
                    bulks_processed += 1
                logger.debug(
                    f'Bulk number {bulks_processed} processed, already processed docs {cnt}.')
                if len(not_ok):
                    logger.error(
                        f'NOK DOCUMENTS (log limited to 10) in batch {bulks_processed}: {not_ok[-10:]}')
                    not_ok = []
            logger.info(
                f'Refreshing index {self.elastic.es_index_name} to make indexed documents searchable.')
            self.elastic.indices.refresh(index=index_name)
        except Exception as e:
            logger.info(
                f'Error when bulking: {e}')
            backoff(self.load_data(transformed_data, chunk_size))
        else:
            return cnt + 1


@lru_cache()
def get_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> Service:
    return Service(redis, elastic)


def create_index(client, index_name):
    func_name = 'create_index_' + index_name
    eval(func_name(client, index_name))


def create_index_genres(client, index_name):
    created = False
    settings = {
        'settings': {
            'refresh_interval': '1s',
            'analysis':
                {
                    'filter': {
                        'english_stop': {
                            'type': 'stop',
                            'stopwords': '_english_'
                        },
                        'english_stemmer': {
                            'type': 'stemmer',
                            'language': 'english'
                        },
                        'english_possessive_stemmer': {
                            'type': 'stemmer',
                            'language': 'possessive_english'
                        },
                        'russian_stop': {
                            'type': 'stop',
                            'stopwords': '_russian_'
                        },
                        'russian_stemmer': {
                            'type': 'stemmer',
                            'language': 'russian'
                        }
                    },
                    'analyzer': {
                        'ru_en': {
                            'tokenizer': 'standard',
                            'filter': [
                                'lowercase',
                                'english_stop',
                                'english_stemmer',
                                'english_possessive_stemmer',
                                'russian_stop',
                                'russian_stemmer'
                            ]
                        }
                    }
                },

            'mappings':
                {
                    'dynamic': 'strict',
                    'properties': {
                        'id': {
                            'type': 'keyword'
                        },
                        'name': {
                            'type': 'text',
                            'analyzer': 'ru_en',
                            'fields': {
                                'raw': {
                                    'type': 'keyword'
                                }
                            }
                        },
                    }
                }
        }
    }
    try:
        if not client.indices.exists(index_name):
            # Ignore 400 means to ignore "Index Already Exist" error.
            client.indices.create(index=index_name, ignore=400, body=settings)
            print('Created Index')
        created = True
    except Exception as ex:
        print(str(ex))
    finally:
        return created


def create_index_persons(client, index_name):
    created = False
    settings = {
        'settings': {
            'refresh_interval': '1s',
            'analysis':
                {
                    'filter': {
                        'english_stop': {
                            'type': 'stop',
                            'stopwords': '_english_'
                        },
                        'english_stemmer': {
                            'type': 'stemmer',
                            'language': 'english'
                        },
                        'english_possessive_stemmer': {
                            'type': 'stemmer',
                            'language': 'possessive_english'
                        },
                        'russian_stop': {
                            'type': 'stop',
                            'stopwords': '_russian_'
                        },
                        'russian_stemmer': {
                            'type': 'stemmer',
                            'language': 'russian'
                        }
                    },
                    'analyzer': {
                        'ru_en': {
                            'tokenizer': 'standard',
                            'filter': [
                                'lowercase',
                                'english_stop',
                                'english_stemmer',
                                'english_possessive_stemmer',
                                'russian_stop',
                                'russian_stemmer'
                            ]
                        }
                    }
                },

            'mappings': {
                'dynamic': 'strict',
                'properties':
                    {
                        'id': {
                            'type': 'keyword'
                        },
                        'full_name': {
                            'type': 'text',
                            'analyzer': 'ru_en',
                            'fields': {
                                'raw': {
                                    'type': 'keyword'
                                }
                            }
                        },
                    }
            }
        }
    }
    try:
        if not client.indices.exists(index_name):
            # Ignore 400 means to ignore "Index Already Exist" error.
            client.indices.create(index=index_name, ignore=400, body=settings)
            print('Created Index')
        created = True
    except Exception as ex:
        print(str(ex))
    finally:
        return created
