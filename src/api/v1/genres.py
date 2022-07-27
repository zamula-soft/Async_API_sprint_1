from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from src.models.mixins import UUIDMixin
from src.services.genre import GenreService, get_genre_service

router = APIRouter()


class GenreListAPI(UUIDMixin, BaseModel):
    name: str


class GenreAPI(UUIDMixin, BaseModel):
    name: str


@router.get('/', response_model=List[GenreListAPI])
async def genre_list(
    page_size: int = Query(10, description='Number of genres on page'),
    page: int = Query(1, description='Page number'),
    sort: str = Query('', description='Sorting fields (A comma-separated list '
                                      'of "field":"direction(=asc|desc)" '
                                      'pairs. Example: name:desc)'),
    genre: str = Query(None, description='Filter by genre uuid'),
    genre_service: GenreService = Depends(get_genre_service)
) -> List[GenreListAPI]:
    """
    Returns list of genres by the parameters specified in the query.
    Each element of the list is a dict of the GenreListAPI structure.
    """
    genres = await genre_service.all(page_size=page_size, page=page, sort=sort, genre=genre)
    return [GenreListAPI.parse_obj(genre.dict(by_alias=True)) for genre in genres]


@router.get('/search', response_model=List[GenreListAPI])
async def genre_search(
    page_size: int = Query(10, description='Number of genres on page'),
    page: int = Query(1, description='Page number'),
    sort: str = Query('', description='Sorting fields (A comma-separated list '
                                      'of "field":"direction(=asc|desc)" '
                                      'pairs. Example: name:desc)'),
    query: str = Query(None, description='Part of the name (Example: comed )'),
    genre_service: GenreService = Depends(get_genre_service)
) -> List[GenreListAPI]:
    """
    Returns list of genres by the parameters specified in the query.
    Each element of the list is a dict of the GenreListAPI structure.

    Unlike the /films/ endpoint, it contains the "query" parameter.

    Parameter **query**: part of genre's name.
    """
    genres = await genre_service.all(page_size=page_size, page=page, sort=sort, query=query)
    return [GenreListAPI.parse_obj(genre.dict(by_alias=True)) for genre in genres]


@router.get('/{genre_id}', response_model=GenreAPI)
async def genre_details(genre_id: str, genre_service: GenreService = Depends(get_genre_service)) -> GenreAPI:
    """
    Returns the dict with all information about the genre by ID.
    """
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')

    return GenreAPI(**genre.dict(by_alias=True))
