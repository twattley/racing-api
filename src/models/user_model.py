from typing import Optional, List
from src.models.pagination_links import PaginationLinks

from src.models.base_entity import BaseEntity


class UserBase(BaseEntity):
    name: str
    email: str


class UserCreate(BaseEntity):
    pass


class UserRead(BaseEntity):
    id: int
    name: str
    email: str

class UserListResponse(BaseEntity):
    data: List[UserRead]
    links: PaginationLinks
