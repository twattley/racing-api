from fastapi import APIRouter, Depends

from ..models.betting_selections import BettingSelections
from ..services.betting_service import BettingService, get_betting_service

router = APIRouter()


@router.post("/betting/selections")
async def store_betting_selections(
    selections: BettingSelections,
    service: BettingService = Depends(get_betting_service),
):
    return await service.store_betting_selections(selections)
