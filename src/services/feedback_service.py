from fastapi import Depends
from fastapi.datastructures import URL

from src.helpers.pagination import build_pagination_links
from src.models.filters.user_filter import UserFilter
from src.repository.user_repository import UserRepository, get_user_repository


class FeedbackService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_users(self, url: URL, page: int, limit: int, filters: UserFilter):
        users, has_more_data = await self.user_repository.get_filtered_users(
            filters, page, limit
        )
        pagination_links = build_pagination_links(url, limit, page, has_more_data)
        return users, pagination_links

    async def get_user(self, user_id: int):
        return await self.user_repository.get_user_by_id(user_id)

    async def get_user_by_name(self, user_name: str):
        return await self.user_repository.get_user_by_name(user_name)


def get_user_service(user_repository: UserRepository = Depends(get_user_repository)):
    return UserService(user_repository)
