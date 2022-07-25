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
from src.models.genre import Genre

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def all(self, **kwargs) -> List[Optional[Genre]]:
        genres = await self._genres_from_cache(**kwargs)
        if not genres:
            genres = await self._get_genres_from_elastic(**kwargs)
            if not genres:
                return []
            await self._put_genres_to_cache(genres, **kwargs)
        return genres

    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        genre = await self._genre_from_cache(genre_id)
        if not genre:
            genre = await self._get_genre_from_elastic(genre_id)
            if not genre:
                return None
            await self._put_genre_to_cache(genre)

        return genre

    @staticmethod
    async def _make_cache_key(*args, **kwargs) -> str:
        return f'{args}:{json.dumps({"kwargs": kwargs}, sort_keys=True)}'

    @staticmethod
    async def _make_genre_from_es_doc(doc: dict) -> Genre:
        genre = doc['_source'].get('genre')
        if genre and isinstance(genre, str):
            doc['_source']['genre'] = [{'id': item, 'name': item} for item in genre.split(' ')]
        result = Genre(id=doc['_id'], **doc['_source'])
        return result

    async def _get_genre_from_elastic(self, genre_id: str) -> Optional[Genre]:
        try:
            doc = await self.elastic.get(index='genres', id=genre_id)
        except NotFoundError:
            logger.debug(f'An error occurred while trying to find genre in ES (id: {genre_id})')
            return None
        genre = doc['_source'].get('genre')
        if genre and isinstance(genre, str):
            doc['_source']['genre'] = [{'id': item, 'name': item} for item in genre.split(' ')]
        return Genre(id=doc['_id'], **doc['_source'])

    async def _get_genres_from_elastic(self, **kwargs) -> Optional[List[Genre]]:
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
            logger.debug('An error occurred while trying to get genres in ES)')
            return None

        return [await GenreService._make_genre_from_es_doc(doc) for doc in docs['hits']['hits']]

    async def _genre_from_cache(self, genre_id: str) -> Optional[Genre]:
        data = await self.redis.get(genre_id)
        if not data:
            logger.debug(f'The genre was not found in the cache (id: {genre_id})')
            return None

        genre = Genre.parse_raw(data)

        return genre

    async def _genres_from_cache(self, **kwargs) -> Optional[List[Genre]]:
        key = await GenreService._make_cache_key(**kwargs)
        data = await self.redis.get(key)
        if not data:
            logger.debug('Genres was not found in the cache')
            return None

        return [Genre.parse_raw(item) for item in orjson.loads(data)]

    async def _put_genre_to_cache(self, genre: Genre):
        await self.redis.set(genre.uuid, genre.json(by_alias=True), ex=GENRE_CACHE_EXPIRE_IN_SECONDS)

    async def _put_genres_to_cache(self, genres: List[Genre], **search_params):
        key = await GenreService._make_cache_key(**search_params)
        await self.redis.set(key,
                             orjson.dumps([genre.json(by_alias=True) for genre in genres]),
                             ex=GENRE_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
