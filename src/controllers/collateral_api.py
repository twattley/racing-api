from typing import List

from fastapi import APIRouter, Depends

from ..models.collateral_form_data import CollateralFormResponse
from ..services.collateral_service import CollateralService, get_collateral_service

router = APIRouter()


@router.get("collateral/form/by-race-id", response_model=List[CollateralFormResponse])
async def get_todays_races(
    race_date: str,
    race_id: int,
    todays_race_date: str,
    service: CollateralService = Depends(get_collateral_service),
):
    return await service.get_collateral_form_by_id(
        race_date=race_date, race_id=race_id, todays_race_date=todays_race_date
    )
