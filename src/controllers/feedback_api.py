from typing import List, Optional
from fastapi import APIRouter, Depends
from ..services.feedback_service import FeedbackService, get_feedback_service
from ..models.performance_data import TodaysPerformanceDataResponse, TodaysRacesResponse, TodaysRacesResultResponse

router = APIRouter()

@router.get("/feedback/todays-races/by-date", response_model=List[TodaysRacesResponse])
async def get_todays_races(
    date: str,
    service: FeedbackService = Depends(get_feedback_service),
):
    return await service.get_todays_races(date=date)

@router.get("/feedback/todays-races/by-race-id", response_model=List[TodaysPerformanceDataResponse])
async def get_race_by_id_and_date(
    date: str,
    race_id: int,
    service: FeedbackService = Depends(get_feedback_service),
):
    return await service.get_race_by_id(date=date, race_id=race_id)

@router.get("/feedback/todays-races/result/by-race-id", response_model=List[TodaysRacesResultResponse])
async def get_race_result_by_id_and_date(
    date: str,
    race_id: int,
    service: FeedbackService = Depends(get_feedback_service),
):
    return await service.get_race_result_by_id(date=date, race_id=race_id)



