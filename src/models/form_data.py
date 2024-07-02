from datetime import date, datetime
from typing import List, Optional

from .base_entity import BaseEntity


class TodaysHorseFormData(BaseEntity):
    age: int
    horse_sex: str
    days_since_last_ran: Optional[int]
    days_since_performance: Optional[int]
    draw: Optional[int]
    headgear: Optional[str]
    weight_carried: str
    weight_carried_lbs: int
    extra_weight: Optional[int]
    jockey_claim: Optional[int]
    finishing_position: Optional[str]
    total_distance_beaten: Optional[float]
    industry_sp: Optional[str]
    betfair_win_sp: Optional[float]
    betfair_place_sp: Optional[float]
    official_rating: Optional[int]
    ts: Optional[int]
    rpr: Optional[int]
    tfr: Optional[int]
    tfig: Optional[int]
    rating: Optional[int]
    speed_figure: Optional[int]
    rating_diff: Optional[int]
    speed_rating_diff: Optional[int]
    in_play_high: Optional[float]
    in_play_low: Optional[float]
    in_race_comment: Optional[str]
    tf_comment: Optional[str]
    tfr_view: Optional[str]
    race_id: int
    jockey_id: int
    trainer_id: int
    owner_id: int
    sire_id: int
    dam_id: int
    unique_id: str
    race_time: datetime
    race_date: date
    race_title: str
    race_type: Optional[str]
    race_class: Optional[int]
    distance: str
    distance_yards: float
    distance_meters: float
    distance_kilometers: float
    conditions: Optional[str]
    going: Optional[str]
    number_of_runners: Optional[int]
    hcap_range: Optional[str]
    age_range: Optional[str]
    surface: Optional[str]
    total_prize_money: Optional[int]
    first_place_prize_money: Optional[int]
    winning_time: Optional[str]
    time_seconds: Optional[float]
    relative_time: Optional[float]
    relative_to_standard: Optional[str]
    country: Optional[str]
    main_race_comment: Optional[str]
    meeting_id: str
    course_id: int
    course: str
    dam: str
    sire: str
    trainer: str
    jockey: str
    data_type: str
    distance_diff: Optional[float]


class TodaysPerformanceDataResponse(BaseEntity):
    horse_name: str
    horse_id: int
    todays_horse_age: int
    todays_first_places: Optional[int]
    todays_second_places: Optional[int]
    todays_third_places: Optional[int]
    todays_fourth_places: Optional[int]
    number_of_runs: Optional[int]
    todays_betfair_win_sp: Optional[float]
    todays_betfair_place_sp: Optional[float]
    todays_official_rating: Optional[int]
    todays_days_since_last_ran: Optional[int]
    performance_data: List[TodaysHorseFormData]


class TodaysRaceFormData(BaseEntity):
    race_id: int
    course: str
    distance: str
    going: str
    surface: str
    race_class: Optional[int]
    hcap_range: Optional[str]
    age_range: str
    conditions: str
    race_type: Optional[str]
    race_title: str
    race_time: datetime
    race_date: date
    horse_data: List[TodaysPerformanceDataResponse]
