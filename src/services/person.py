import json
from functools import lru_cache
from typing import List, Optional

import orjson
from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from loguru import logger

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.person import Person

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def all(self, **kwargs) -> List[Optional[Person]]:
        persons = await self._persons_from_cache(**kwargs)
        if not persons:
            persons = await self._get_persons_from_elastic(**kwargs)
            if not persons:
                return []
            await self._put_persons_to_cache(persons, **kwargs)
        return persons

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        person = await self._person_from_cache(person_id)
        if not person:
            person = await self._get_person_from_elastic(person_id)
            if not person:
                return None
            await self._put_person_to_cache(person)

        return person

    @staticmethod
    async def _make_cache_key(*args, **kwargs) -> str:
        return f'{args}:{json.dumps({"kwargs": kwargs}, sort_keys=True)}'

    @staticmethod
    async def _make_person_from_es_doc(doc: dict) -> Person:
        person = doc['_source'].get('person')
        if person and isinstance(person, str):
            doc['_source']['person'] = [{'id': item, 'name': item} for item in person.split(' ')]
        result = Person(id=doc['_id'], **doc['_source'])
        return result

    async def _get_person_from_elastic(self, person_id: str) -> Optional[Person]:
        try:
            doc = await self.elastic.get(index='genres', id=person_id)
        except NotFoundError:
            logger.debug(f'An error occurred while trying to find person in ES (id: {person_id})')
            return None
        person = doc['_source'].get('person')
        if person and isinstance(person, str):
            doc['_source']['person'] = [{'id': item, 'name': item} for item in person.split(' ')]
        return Person(id=doc['_id'], **doc['_source'])

    async def _get_persons_from_elastic(self, **kwargs) -> Optional[List[Person]]:
        page_size = kwargs.get('page_size', 10)
        page = kwargs.get('page', 1)
        sort = kwargs.get('sort', '')
        genre = kwargs.get('genre', None)
        query = kwargs.get('query', None)
        body = None
        if genre:
            body = {
                'query': {
                    'query_string': {
                        'default_field': 'genre',
                        'query': genre
                    }
                }
            }
        if query:
            body = {
                'query': {
                    'match': {
                        'title': {
                            'query': query,
                            'fuzziness': 1,
                            'operator': 'and'
                        }
                    }
                }
            }
        try:
            docs = await self.elastic.search(index='genres',
                                             body=body,
                                             params={
                                                 'size': page_size,
                                                 'from': page - 1,
                                                 'sort': sort,
                                             })
        except NotFoundError:
            logger.debug('An error occurred while trying to get persons in ES)')
            return None

        return [await PersonService._make_person_from_es_doc(doc) for doc in docs['hits']['hits']]

    async def _person_from_cache(self, person_id: str) -> Optional[Person]:
        data = await self.redis.get(person_id)
        if not data:
            logger.debug(f'The genre was not found in the cache (id: {person_id})')
            return None

        return Person.parse_raw(data)

    async def _persons_from_cache(self, **kwargs) -> Optional[List[Person]]:
        key = await PersonService._make_cache_key(**kwargs)
        data = await self.redis.get(key)
        if not data:
            logger.debug('Persons was not found in the cache')
            return None

        return [Person.parse_raw(item) for item in orjson.loads(data)]

    async def _put_person_to_cache(self, person: Person):
        await self.redis.set(person.uuid, person.json(by_alias=True), ex=PERSON_CACHE_EXPIRE_IN_SECONDS)

    async def _put_persons_to_cache(self, persons: List[Person], **search_params):
        key = await PersonService._make_cache_key(**search_params)
        await self.redis.set(key,
                             orjson.dumps([person.json(by_alias=True) for person in persons]),
                             ex=PERSON_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
