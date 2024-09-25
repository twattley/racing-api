from typing import List

from .base_entity import BaseEntity


class BettingSelection(BaseEntity):
    horse_id: int
    bet_type: str


class BettingSelections(BaseEntity):
    race_date: str
    race_id: int
    selections: List[BettingSelection]
