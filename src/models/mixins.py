import orjson
from pydantic import BaseModel, Field

from src.models.utils import orjson_dumps


class UUIDMixin(BaseModel):
    uuid: str = Field(alias='id')


class OrjsonConfigMixin(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
