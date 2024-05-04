from typing import Optional
from pydantic import BaseModel

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


class UserUpdate(BaseEntity):
    name: Optional[str] = None
    email: Optional[str] = None
