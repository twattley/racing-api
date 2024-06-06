from typing import List, Optional

from fastapi import APIRouter, Depends

from ..models.feedback_date import DateRequest, TodaysFeedbackDateResponse
from ..models.feedback_result import TodaysRacesResultResponse
from ..models.form_data import TodaysRaceFormData
from ..models.form_graph import TodaysHorseGraphData
from ..models.todays_race_times import TodaysRacesResponse
from ..services.feedback_service import FeedbackService, get_feedback_service

router = APIRouter()


@router.get("/feedback/todays-races/by-date", response_model=List[TodaysRacesResponse])
async def get_todays_races(
    date: str,
    service: FeedbackService = Depends(get_feedback_service),
):
    return await service.get_todays_races(date=date)


@router.get(
    "/feedback/todays-races/current-date", response_model=TodaysFeedbackDateResponse
)
async def get_current_date_today(
    service: FeedbackService = Depends(get_feedback_service),
):
    data = await service.get_current_date_today()
    return {
        "today_date": data["today_date"],
        "success": True,
        "message": "Date fetched successfully",
    }


@router.post(
    "/feedback/todays-races/selected-date", response_model=TodaysFeedbackDateResponse
)
async def store_current_date_today(
    date_request: DateRequest,
    service: FeedbackService = Depends(get_feedback_service),
):
    date = date_request.date
    data = await service.store_current_date_today(date=date)
    return {
        "today_date": data["today_date"],
        "success": True,
        "message": "Date stored successfully",
    }


@router.get("/feedback/todays-races/by-race-id", response_model=TodaysRaceFormData)
async def get_race_by_id_and_date(
    race_id: int,
    date: Optional[str] = None,
    service: FeedbackService = Depends(get_feedback_service),
):
    if date is None:
        date = (await service.get_current_date_today())["today_date"]
    return await service.get_race_by_id(date=date, race_id=race_id)


@router.get(
    "/feedback/todays-races/graph/by-race-id",
    response_model=List[TodaysHorseGraphData],
)
async def get_race_graph_by_id_and_date(
    race_id: int,
    date: Optional[str] = None,
    service: FeedbackService = Depends(get_feedback_service),
):
    if date is None:
        date = (await service.get_current_date_today())["today_date"]
    return await service.get_race_graph_by_id(date=date, race_id=race_id)


@router.get(
    "/feedback/todays-races/result/by-race-id",
    response_model=List[TodaysRacesResultResponse],
)
async def get_race_result_by_id_and_date(
    race_id: int,
    date: Optional[str] = None,
    service: FeedbackService = Depends(get_feedback_service),
):
    if date is None:
        date = (await service.get_current_date_today())["today_date"]
    return await service.get_race_result_by_id(date=date, race_id=race_id)
