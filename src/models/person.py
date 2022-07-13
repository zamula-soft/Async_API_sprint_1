import orjson
from pydantic import Field

from src.models.mixins import UUIDMixin
from src.models.utils import orjson_dumps


class Person(UUIDMixin):
    full_name: str = Field(alias='name')

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
