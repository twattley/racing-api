from typing import List

from fastapi import APIRouter, Depends

from ..models.feedback_date import DateRequest, TodaysFeedbackDateResponse
from ..models.feedback_result import TodaysRacesResultResponse
from ..models.form_data import TodaysRaceFormData
from ..models.todays_race_times import TodaysRacesResponse
from ..services.feedback_service import FeedbackService, get_feedback_service

router = APIRouter()


@router.get(
    "/feedback/todays-races/current-date", response_model=TodaysFeedbackDateResponse
)
async def get_current_date_today(
    feedback_service: FeedbackService = Depends(get_feedback_service),
):
    data = await feedback_service.get_current_date_today()
    return {
        "today_date": data["today_date"].astype(str).iloc[0],
        "success": True,
        "message": "Date fetched successfully",
    }


@router.post("/feedback/todays-races/selected-date")
async def store_current_date_today(
    date_request: DateRequest,
    feedback_service: FeedbackService = Depends(get_feedback_service),
):
    date = date_request.date
    await feedback_service.store_current_date_today(date=date)
    return {
        "today_date": date,
        "success": True,
        "message": "Date stored successfully",
    }


@router.get("/feedback/todays-races/by-date", response_model=List[TodaysRacesResponse])
async def get_todays_races(
    feedback_service: FeedbackService = Depends(get_feedback_service),
):
    return await feedback_service.get_todays_races()


@router.get("/feedback/todays-races/by-race-id", response_model=TodaysRaceFormData)
async def get_race_by_id_and_date(
    race_id: int,
    feedback_service: FeedbackService = Depends(get_feedback_service),
):
    return await feedback_service.get_race_by_id(race_id=race_id)


@router.get(
    "/feedback/todays-races/result/by-race-id",
    response_model=List[TodaysRacesResultResponse],
)
async def get_race_result_by_id_and_date(
    race_id: int,
    feedback_service: FeedbackService = Depends(get_feedback_service),
):
    return await feedback_service.get_race_result_by_id(race_id=race_id)
