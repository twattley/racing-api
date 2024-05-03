from pydantic import ConfigDict

from src.models.base_entity import BaseEntity


class AbstractFilter(BaseEntity):
    tenant_id: str | None = None
    model_config = ConfigDict(populate_by_name=True, extra="allow")
