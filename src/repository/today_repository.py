from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.helpers.session_manager import get_current_session
from src.models.db.user_schema import UserSchema
from src.models.filters.user_filter import UserFilter
from src.repository.base_repository import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_filtered_users(self, filters: UserFilter, page: int, limit: int):
        query = select(UserSchema)
        query = filters.filter(query)
        result = await self.session.execute(
            query.offset((page - 1) * limit).limit(limit)
        )
        users = result.scalars().all()

        has_more_data = len(users) == limit
        return users, has_more_data

    async def get_user_by_id(self, user_id: int):
        query = select(UserSchema).where(UserSchema.id == user_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_user_by_name(self, user_name: str):
        query = select(UserSchema).where(UserSchema.name == user_name)
        result = await self.session.execute(query)
        return result.scalars().first()


def get_user_repository(session: AsyncSession = Depends(get_current_session)):
    return UserRepository(session)
