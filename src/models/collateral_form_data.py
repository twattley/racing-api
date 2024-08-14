from .base_entity import BaseEntity
from typing import List, Optional, Dict
from datetime import datetime, date
from decimal import Decimal


class CollateralFormData(BaseEntity):
    official_rating: int
    finishing_position: str
    total_distance_beaten: Decimal
    betfair_win_sp: Decimal
    rating: int
    speed_figure: int
    horse_id: int
    unique_id: str
    race_id: int
    race_time: datetime
    race_date: date
    race_type: str
    race_class: int
    distance: str
    conditions: str
    going: str
    number_of_runners: int
    surface: str
    main_race_comment: str
    tf_comment: str
    tfr_view: str | None


class HorseCollateralData(BaseEntity):
    horse_id: int
    horse_name: str
    distance_difference: Decimal
    betfair_win_sp: Decimal
    official_rating: int
    collateral_form_data: List[CollateralFormData]


class CollateralFormResponse(BaseEntity):
    horse_collateral_data: List[HorseCollateralData]
