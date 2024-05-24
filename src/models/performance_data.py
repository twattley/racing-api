from datetime import date, datetime
from typing import List, Optional
from ..models.base_entity import BaseEntity

class TodaysRaceData(BaseEntity):
    race_id: int
    race_time: datetime
    race_title: str
    race_type: str
    race_class: Optional[int]
    distance: str
    distance_yards: float
    distance_meters: float
    distance_kilometers: float
    conditions: str
    going: str
    number_of_runners: int
    hcap_range: Optional[str]
    age_range: str
    surface: str
    total_prize_money: int
    first_place_prize_money: int

class TodaysCourseData(BaseEntity):
    course: str
    course_id: int
    races: List[TodaysRaceData]

class TodaysRacesResponse(BaseEntity):
    race_date: date
    courses: List[TodaysCourseData]

class HorseFormData(BaseEntity):
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
    number_of_runs: Optional[int]
    first_places : Optional[int]
    second_places : Optional[int]
    third_places : Optional[int]
    fourth_places : Optional[int]
    total_distance_beaten: Optional[float]
    industry_sp: Optional[str]
    betfair_win_sp: Optional[float]
    betfair_place_sp: Optional[float]
    official_rating: Optional[int]
    ts: Optional[int]
    rpr: Optional[int]
    tfr: Optional[int]
    tfig: Optional[int]
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
    race_type: str
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

class TodaysPerformanceDataResponse(BaseEntity):
    horse_name: str
    horse_id: int
    list: List[HorseFormData]

class TodaysRacesResultHorseDataResponse(BaseEntity):
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
    race_results: List[TodaysRacesResultHorseDataResponse]


