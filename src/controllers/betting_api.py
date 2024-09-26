from typing import List
from fastapi import APIRouter, Depends

from ..models.betting_selections import BettingSelections, BettingSelectionsAnalysis
from ..services.betting_service import BettingService, get_betting_service

router = APIRouter()


@router.post("/betting/selections")
async def store_betting_selections(
    selections: BettingSelections,
    service: BettingService = Depends(get_betting_service),
):
    return await service.store_betting_selections(selections)


@router.get("/betting/selections_analysis")
async def get_betting_selections_analysis(
    service: BettingService = Depends(get_betting_service),
) -> List[BettingSelectionsAnalysis]:
    return await service.get_betting_selections_analysis()
