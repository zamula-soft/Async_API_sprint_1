from typing import List

from src.models.genre import Genre
from src.models.mixins import UUIDMixin, OrjsonConfigMixin
from src.models.person import Person


class Film(UUIDMixin, OrjsonConfigMixin):
    title: str
    imdb_rating: float
    description: str = ''
    genre: List[Genre] = []
    actors: List[Person] = []
    writers: List[Person] = []
    directors: List[Person] = []
