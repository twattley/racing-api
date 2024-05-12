from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.helpers.postgres import get_current_session
from src.repository.base_repository import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_users(self, page: int = 1, limit: int = 10):
        offset = (page - 1) * limit
        query = text("SELECT * FROM users ORDER BY id LIMIT :limit OFFSET :offset")
        result = await self.session.execute(query, {"limit": limit, "offset": offset})
        users = [dict(row) for row in result.mappings().all()]

        # Determine if there's more data
        next_page_query = text(
            "SELECT 1 FROM users ORDER BY id LIMIT 1 OFFSET :next_offset"
        )
        next_page_result = await self.session.execute(
            next_page_query, {"next_offset": offset + limit}
        )
        has_more_data = next_page_result.scalar() is not None

        return users, has_more_data

    async def get_user_by_id(self, user_id: int):
        async with self.session.begin():
            query = text("SELECT * FROM users WHERE id = :user_id")
            result = await self.session.execute(query, {"user_id": user_id})
            return dict(result.mappings().first())

    async def get_user_by_name(self, user_name: str):
        async with self.session.begin():
            query = text("SELECT * FROM users WHERE name = :user_name")
            result = await self.session.execute(query, {"user_name": user_name})
            return dict(result.mappings().first())


def get_user_repository(session: AsyncSession = Depends(get_current_session)):
    return UserRepository(session)
