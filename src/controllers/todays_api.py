from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends

from ..models.form_data import TodaysRaceFormData
from ..models.form_graph import TodaysHorseGraphData
from ..models.todays_race_times import TodaysRacesResponse
from ..services.todays_service import TodaysService, get_todays_service

router = APIRouter()


@router.get("/today/todays-races/by-date", response_model=List[TodaysRacesResponse])
async def get_todays_races(
    date: str,
    service: TodaysService = Depends(get_todays_service),
):
    return await service.get_todays_races(date=date)


@router.get("/today/todays-races/by-race-id", response_model=TodaysRaceFormData)
async def get_race_by_id_and_date(
    race_id: int,
    service: TodaysService = Depends(get_todays_service),
):
    return await service.get_race_by_id(
        date=datetime.now().strftime("%Y-%m-%d"), race_id=race_id
    )


@router.get(
    "/today/todays-races/graph/by-race-id",
    response_model=List[TodaysHorseGraphData],
)
async def get_race_graph_by_id(
    race_id: int,
    service: TodaysService = Depends(get_todays_service),
):
    return await service.get_race_graph_by_id(
        date=datetime.now().strftime("%Y-%m-%d"), race_id=race_id
    )