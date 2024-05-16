from fastapi import Query
from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic.fields import Field

from src.models.db.user_schema import UserSchema


class FeedbackFilter(Filter):
    id: int | None = Field(Query(default=None, alias="filter[id]"))
    id__in: list[int] | None = Field(Query(default=None, alias="filter[id__in]"))
    name: str | None = Field(Query(default=None, alias="filter[name]"))
    name__in: list[str] | None = Field(Query(default=None, alias="filter[name__in]"))
    email: str | None = Field(Query(default=None, alias="filter[email]"))
    email__in: list[str] | None = Field(Query(default=None, alias="filter[email__in]"))

    class Constants(Filter.Constants):
        model = UserSchema
