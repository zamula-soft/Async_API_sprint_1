from pydantic import Field

from src.models.mixins import OrjsonConfigMixin, UUIDMixin


class Person(UUIDMixin, OrjsonConfigMixin):
    full_name: str = Field(alias='name')
