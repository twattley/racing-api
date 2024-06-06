from datetime import date, datetime
from typing import List, Optional

from .base_entity import BaseEntity


class TodaysGraphPerformanceData(BaseEntity):
    race_time: datetime
    race_date: date
    official_rating: Optional[int]
    ts: Optional[int]
    rpr: Optional[int]
    tfr: Optional[int]
    tfig: Optional[int]
    race_id: int
    unique_id: str


class TodaysHorseGraphData(BaseEntity):
    horse_name: str
    horse_id: int
    performance_data: List[TodaysGraphPerformanceData]
