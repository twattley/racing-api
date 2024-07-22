from typing import List

from fastapi import APIRouter, Depends

from ..models.form_data import TodaysRaceFormData
from ..models.todays_race_times import TodaysRacesResponse
from ..services.todays_service import TodaysService, get_todays_service

router = APIRouter()


@router.get("/today/todays-races/by-date", response_model=List[TodaysRacesResponse])
async def get_todays_races(
    today_service: TodaysService = Depends(get_todays_service),
):
    return await today_service.get_todays_races()


@router.get("/today/todays-races/by-race-id", response_model=TodaysRaceFormData)
async def get_race_by_id(
    race_id: int,
    today_service: TodaysService = Depends(get_todays_service),
):
    return await today_service.get_race_by_id(race_id=race_id)
