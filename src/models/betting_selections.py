from datetime import date, datetime
from typing import List, Optional

from .base_entity import BaseEntity


class BettingSelection(BaseEntity):
    horse_id: int
    bet_type: str


class BettingSelections(BaseEntity):
    race_date: str
    race_id: int
    selections: List[BettingSelection]


class BettingSelectionsAnalysis(BaseEntity):
    betting_type: str
    horse_name: str
    age: int
    horse_sex: str
    finishing_position: str
    total_distance_beaten: float
    betfair_win_sp: float
    betfair_place_sp: float
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
    horse_id: int
    jockey_id: Optional[int]
    trainer_id: Optional[int]
    owner_id: Optional[int]
    sire_id: Optional[int]
    dam_id: Optional[int]
    unique_id: Optional[str]
    race_time: Optional[datetime]
    race_date: Optional[date]
    race_title: Optional[str]
    race_type: Optional[str]
    race_class: Optional[int]
    distance: Optional[str]
    race_class: Optional[int]
    distance: Optional[str]
    distance_yards: Optional[float]
    conditions: Optional[str]
    going: Optional[str]
    number_of_runners: Optional[int]
    hcap_range: Optional[str]
    age_range: Optional[str]
    surface: Optional[str]
    country: Optional[str]
    main_race_comment: Optional[str]
    meeting_id: str
    course_id: Optional[int]
    course: Optional[str]
    dam: Optional[str]
    sire: Optional[str]
    trainer: Optional[str]
    jockey: Optional[str]
    price_move: Optional[float]
    final_odds: Optional[float]
    adjusted_final_odds: Optional[float]
    bet_result: Optional[float]
