from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from src.models.mixins import UUIDMixin
from src.services.person import PersonService, get_person_service

router = APIRouter()


class PersonListAPI(UUIDMixin, BaseModel):
    full_name: str


class PersonAPI(UUIDMixin, BaseModel):
    full_name: str


@router.get('/', response_model=List[PersonListAPI])
async def person_list(
    page_size: int = Query(10, description='Number of persons on page'),
    page: int = Query(1, description='Page number'),
    sort: str = Query('', description='Sorting fields (A comma-separated list '
                                      'of "field":"direction(=asc|desc)" '
                                      'pairs. Example: name:desc)'),
    genre: str = Query(None, description='Filter by genre uuid'), # may be delete
    person_service: PersonService = Depends(get_person_service)
) -> List[PersonListAPI]:
    persons = await person_service.all(page_size=page_size, page=page, sort=sort, genre=genre)
    return [PersonListAPI.parse_obj(person.dict(by_alias=True)) for person in persons]


@router.get('/search', response_model=List[PersonListAPI])
async def person_search(
    page_size: int = Query(10, description='Number of persons on page'),
    page: int = Query(1, description='Page number'),
    sort: str = Query('', description='Sorting fields (A comma-separated list '
                                      'of "field":"direction(=asc|desc)" '
                                      'pairs. Example: name:desc)'),
    query: str = Query(None, description='Part of the full-name (Example: Jame )'),
    person_service: PersonService = Depends(get_person_service)
) -> List[PersonListAPI]:
    persons = await person_service.all(page_size=page_size, page=page, sort=sort, query=query)
    return [PersonListAPI.parse_obj(person.dict(by_alias=True)) for person in persons]


@router.get('/{person_id}', response_model=PersonAPI)
async def person_details(person_id: str, person_service: PersonService = Depends(get_person_service)) -> PersonAPI:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Person not found')

    return PersonAPI(**person.dict(by_alias=True))
