from fastapi import Depends

from src.models.betting_selections import BettingSelections

from ..repository.betting_repository import (
    BettingRepository,
    get_betting_repository,
)
from .base_service import BaseService


class BettingService(BaseService):
    def __init__(
        self,
        betting_repository: BettingRepository,
    ):
        self.betting_repository = betting_repository

    async def store_betting_selections(self, selections: BettingSelections):
        await self.betting_repository.store_betting_selections(selections)


def get_betting_service(
    betting_repository: BettingRepository = Depends(get_betting_repository),
):
    return BettingService(betting_repository)
