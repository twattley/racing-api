from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.user_service import UserService
from src.daos.user_dao import UserDAO
from src.helpers.postgres import get_current_session
from typing import List
from src.models.user_model import UserRead

router = APIRouter()

# Dependency to provide session for each request
def get_dao(session: AsyncSession = Depends(get_current_session)):
    return UserDAO(session)

@router.get("/users/", response_model=List[UserRead])
async def read_all_users(user_dao: UserDAO = Depends(get_dao)):
    user_service = UserService(user_dao)
    return await user_service.get_users()

@router.get("/users/{user_id}", response_model=UserRead)
async def read_user(user_id: int, user_dao: UserDAO = Depends(get_dao)):
    user_service = UserService(user_dao)
    return await user_service.get_user(user_id)

@router.get("/users/name/{user_name}")
async def read_user(user_name: str, user_dao: UserDAO = Depends(get_dao)) -> UserRead:
    user_service = UserService(user_dao)
    return await user_service.get_user_by_name(user_name)
