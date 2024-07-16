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
    rating: Optional[int]
    speed_figure: Optional[int]
    rolling_rating: Optional[int]
    rolling_speed_rating: Optional[int]
    race_id: int
    unique_id: str


class TodaysHorseGraphData(BaseEntity):
    horse_name: str
    horse_id: int
    initial_visibility: bool
    performance_data: List[TodaysGraphPerformanceData]
