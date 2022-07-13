from typing import List

import orjson

from src.models.genre import Genre
from src.models.mixins import UUIDMixin
from src.models.person import Person
from src.models.utils import orjson_dumps


class Film(UUIDMixin):
    title: str
    imdb_rating: float
    description: str = ''
    genre: List[Genre] = []
    actors: List[Person] = []
    writers: List[Person] = []
    directors: List[Person] = []

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
