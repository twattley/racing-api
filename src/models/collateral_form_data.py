from datetime import date, datetime
from typing import Optional

from .base_entity import BaseEntity


class CollateralFormResponse(BaseEntity):
    age: int
    horse_sex: str
    days_since_last_ran: Optional[int]
    days_since_performance: Optional[int]
    weeks_since_last_ran: Optional[int]
    weeks_since_performance: Optional[int]
