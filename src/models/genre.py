import orjson

from src.models.mixins import UUIDMixin
from src.models.utils import orjson_dumps


class Genre(UUIDMixin):
    name: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
