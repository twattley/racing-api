from typing import Protocol, runtime_checkable

from sqlalchemy.ext.asyncio import AsyncSession


@runtime_checkable
class BaseRepository(Protocol):
    def __init__(self, session: AsyncSession):
        pass

    async def get_all_users(self):
        pass

    async def get_user_by_id(self, user_id: int):
        pass

    async def get_user_by_name(self, user_name: str):
        pass
