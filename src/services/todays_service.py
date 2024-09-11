from datetime import datetime
from fastapi import Depends


from ..repository.todays_repository import TodaysRepository, get_todays_repository
from .base_service import BaseService
from .transformation_service import TransformationService


class TodaysService(BaseService):
    todays_repository: TodaysRepository
    transformation_service: TransformationService

    def __init__(
        self,
        todays_repository: TodaysRepository,
        transformation_service: TransformationService,
    ):
        self.todays_repository = todays_repository
        self.transformation_service = transformation_service

    async def get_todays_races(self):
        data = await self.todays_repository.get_todays_races()
        return self.format_todays_races(data[data["race_time"] >= datetime.now()])

    async def get_race_by_id(self, race_id: int):
        todays_data = await self.todays_repository.get_race_by_id(race_id)
        return self.format_todays_form_data(
            todays_data,
            self.transformation_service.calculate,
        )


def get_todays_service(
    todays_repository: TodaysRepository = Depends(get_todays_repository),
):
    transformation_service = TransformationService()
    return TodaysService(todays_repository, transformation_service)
