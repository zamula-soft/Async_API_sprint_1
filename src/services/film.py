from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from loguru import logger

from src.core.config import settings
from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        logger.debug(f'REDIS_HOST = {settings.REDIS_HOST}')
        logger.debug(f'ELASTIC_HOST = {settings.ELASTIC_HOST}')
        film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)

        return film

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get(index='movies', id=film_id)
        except NotFoundError:
            logger.debug(f'An error occurred while trying to find film in ES (id: {film_id})')
            return None
        genre = doc['_source'].get('genre')
        if genre and isinstance(genre, str):
            doc['_source']['genre'] = [{'id': item, 'name': item} for item in genre.split(' ')]
        return Film(id=doc['_id'], **doc['_source'])

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        data = await self.redis.get(film_id)
        if not data:
            logger.debug(f'The film was not found in the cache (id: {film_id})')
            return None

        film = Film.parse_raw(data)

        return film

    async def _put_film_to_cache(self, film: Film):
        await self.redis.set(film.uuid, film.json(by_alias=True), ex=FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
