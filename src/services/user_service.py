from src.daos.user_dao import UserDAO

class UserService:
    def __init__(self, user_dao: UserDAO):
        self.user_dao = user_dao

    async def get_users(self):
        return await self.user_dao.get_all_users()

    async def get_user(self, user_id: int):
        return await self.user_dao.get_user_by_id(user_id)
    
    async def get_user_by_name(self, user_name: str):
        return await self.user_dao.get_user_by_name(user_name)
