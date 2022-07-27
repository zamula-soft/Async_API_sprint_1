from pydantic import Field

from src.models.mixins import UUIDMixin, OrjsonConfigMixin


class Person(UUIDMixin, OrjsonConfigMixin):
    full_name: str = Field(alias='name')
