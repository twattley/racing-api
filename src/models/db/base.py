from typing import Any

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    def get(self, key) -> Any:
        return getattr(self, key)
