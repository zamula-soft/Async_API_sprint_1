from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.models.film import Genre, Person
from src.models.mixins import UUIDMixin
from src.services.film import FilmService, get_film_service

router = APIRouter()


class FilmAPI(UUIDMixin, BaseModel):
    title: str
    imdb_rating: float
    description: str
    genre: List[Genre]
    actors: List[Person]
    writers: List[Person]
    directors: List[Person]


@router.get('/{film_id}', response_model=FilmAPI)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> FilmAPI:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    return FilmAPI.parse_obj(film.dict(by_alias=True))
