from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from src.models.film import Genre, Person
from src.models.mixins import UUIDMixin
from src.services.film import FilmService, get_film_service

router = APIRouter()


class FilmListAPI(UUIDMixin, BaseModel):
    title: str
    imdb_rating: float
    genre: List[Genre]


class FilmAPI(UUIDMixin, BaseModel):
    title: str
    imdb_rating: float
    description: str
    genre: List[Genre]
    actors: List[Person]
    writers: List[Person]
    directors: List[Person]


@router.get('/', response_model=List[FilmListAPI])
async def film_list(
    page_size: int = Query(10, description='Number of films on page'),
    page: int = Query(1, description='Page number'),
    sort: str = Query('', description='Sorting fields (A comma-separated list '
                                      'of "field":"direction(=asc|desc)" '
                                      'pairs. Example: imdb_rating:desc)'),
    genre: str = Query(None, description='Filter by genre uuid'),
    film_service: FilmService = Depends(get_film_service)
) -> List[FilmListAPI]:
    films = await film_service.all(page_size=page_size, page=page, sort=sort, genre=genre)
    return [FilmListAPI.parse_obj(film.dict(by_alias=True)) for film in films]


@router.get('/search', response_model=List[FilmListAPI])
async def film_search(
    page_size: int = Query(10, description='Number of films on page'),
    page: int = Query(1, description='Page number'),
    sort: str = Query('', description='Sorting fields (A comma-separated list '
                                      'of "field":"direction(=asc|desc)" '
                                      'pairs. Example: imdb_rating:desc)'),
    query: str = Query(None, description='Part of the movie title (Example: dark sta )'),
    film_service: FilmService = Depends(get_film_service)
) -> List[FilmListAPI]:
    films = await film_service.all(page_size=page_size, page=page, sort=sort, query=query)
    return [FilmListAPI.parse_obj(film.dict(by_alias=True)) for film in films]


@router.get('/{film_id}', response_model=FilmAPI)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> FilmAPI:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    return FilmAPI(**film.dict(by_alias=True))
