from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.db.user_schema import UserSchema

class UserDAO:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_users(self):
        async with self.session.begin():
            result = await self.session.execute(select(UserSchema))
            return result.scalars().all()

    async def get_user_by_id(self, user_id: int):
        async with self.session.begin():
            result = await self.session.execute(select(UserSchema).where(UserSchema.id == user_id))
            return result.scalars().first()
