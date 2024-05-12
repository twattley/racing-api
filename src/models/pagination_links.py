from pydantic import AnyUrl

from src.models.base_entity import BaseEntity


class PaginationLinks(BaseEntity):
    self: AnyUrl
    prev: AnyUrl | None = None
    next: AnyUrl | None = None
