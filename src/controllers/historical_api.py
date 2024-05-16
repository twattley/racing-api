from typing import List

from fastapi import APIRouter, Depends, Query, Request
from src.models.filters.user_filter import UserFilter
from fastapi_filter import FilterDepends
from src.models.user_model import UserListResponse, UserRead  
from src.services.user_service import UserService, get_user_service

router = APIRouter()
@router.get("/results", response_model=UserListResponse)
async def read_all_results(
    request: Request,
    page: int = Query(1, ge=1, description="Page number starting from 1"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page, up to 100"),
    filters: UserFilter = FilterDepends(UserFilter),
    service: UserService = Depends(get_user_service),
):
    users, pagination_links = await service.get_users(
        url=request.url, page=page, limit=limit, filters=filters
    )
    return {"data": users, "links": pagination_links.dict()}


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
