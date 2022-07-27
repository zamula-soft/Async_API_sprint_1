from src.models.mixins import OrjsonConfigMixin, UUIDMixin


class Genre(UUIDMixin, OrjsonConfigMixin):
    name: str
