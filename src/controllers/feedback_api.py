from typing import List

from fastapi import APIRouter, Depends, Query, Request
from fastapi_filter import FilterDepends
from src.models.performance_data import TodaysRacesResponse


from src.services.user_service import UserService, get_user_service



router = APIRouter()


@router.get("/results/feedback/{date}", response_model=TodaysRacesResponse)
async def get_todays_races(
    date: str,
    service: FeedbackService = Depends(get_feedback_service),
):
    return await service.get_todays_races(date=date)



@router.get("/users/{user_id}", response_model=UserRead)
async def read_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
):
    return await service.get_user(user_id)


@router.get("/users/name/{user_name}")
async def read_user(
    user_name: str,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    return await service.get_user_by_name(user_name)
