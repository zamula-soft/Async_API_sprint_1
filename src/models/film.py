from src.models.genre import Genre
from src.models.mixins import UUIDMixin, OrjsonConfigMixin
from src.models.person import Person


class Film(UUIDMixin, OrjsonConfigMixin):
    title: str
    imdb_rating: float
    description: str = ''
    genre: list[Genre] = []
    actors: list[Person] = []
    writers: list[Person] = []
    directors: list[Person] = []
