from pydantic import BaseModel, Field


class UUIDMixin(BaseModel):
    uuid: str = Field(alias='id')
