from datetime import date, datetime
from typing import List, Optional

from .base_entity import BaseEntity


class CollateralFormData(BaseEntity):
    official_rating: Optional[int]
    finishing_position: str
    total_distance_beaten: float
    betfair_win_sp: float
    rating: Optional[int]
    speed_figure: int
    horse_id: int
    unique_id: str
    race_id: int
    race_time: datetime
    race_date: date
    race_type: Optional[str]
    race_class: Optional[int]
    distance: Optional[str]
    conditions: Optional[str]
    going: Optional[str]
    number_of_runners: Optional[int]
    surface: Optional[str]
    main_race_comment: Optional[str]
    tf_comment: Optional[str]
    tfr_view: Optional[str]


class HorseCollateralData(BaseEntity):
    horse_id: int
    horse_name: str
    distance_difference: float
    betfair_win_sp: float
    official_rating: Optional[int]
    collateral_form_data: List[CollateralFormData]


class CollateralFormResponse(BaseEntity):
    average_collateral_rating: int
    important_result_count: int
    valid_collateral_performance_count: int
    horse_collateral_data: List[HorseCollateralData]
