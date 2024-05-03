from datetime import datetime
from typing import Any

from pydantic import BaseModel, field_validator

from src.models.validators.time_zone_validator import validate_has_timezone


class BaseEntity(BaseModel):
    def dict(self, *args, **kwargs) -> dict[str, Any]:
        kwargs.pop("exclude_none", None)
        return super().model_dump(*args, **kwargs, exclude_none=True)

    @field_validator("*")
    @classmethod
    def validate_datetime_field(cls, field):
        if field is not None and isinstance(field, datetime):
            return validate_has_timezone(field)

        return field

    def get_id(self):
        raise NotImplementedError("Method is not implemented")

    def get_pk_fields(self) -> list[str]: ...

    class Config:
        from_attributes = True
