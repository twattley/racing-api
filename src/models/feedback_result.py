from datetime import date, datetime
from typing import List, Optional

from ..models.base_entity import BaseEntity


class TodaysRacesResultDataResponse(BaseEntity):
    horse_name: str
    horse_id: int
    age: int
    draw: Optional[int]
    headgear: Optional[str]
    weight_carried: Optional[str]
    finishing_position: Optional[str]
    total_distance_beaten: Optional[float]
    betfair_win_sp: Optional[float]
    official_rating: Optional[int]
    ts: Optional[int]
    rpr: Optional[int]
    tfr: Optional[int]
    tfig: Optional[int]
    in_play_high: Optional[float]
    in_play_low: Optional[float]
    tf_comment: Optional[str]
    tfr_view: Optional[str]


class TodaysRacesResultResponse(BaseEntity):
    race_time: datetime
    race_date: date
    race_title: str
    race_type: Optional[str]
    race_class: Optional[int]
    distance: str
    conditions: str
    going: str
    number_of_runners: int
    hcap_range: Optional[str]
    age_range: Optional[str]
    surface: Optional[str]
    total_prize_money: Optional[int]
    winning_time: Optional[str]
    relative_time: Optional[float]
    relative_to_standard: Optional[str]
    main_race_comment: Optional[str]
    course_id: int
    course: str
    race_id: int
    race_results: List[TodaysRacesResultDataResponse]
