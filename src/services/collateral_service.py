from fastapi import Depends

from ..repository.collateral_repository import (
    CollateralRepository,
    get_collateral_repository,
)
from .base_service import BaseService
from .transformation_service import TransformationService


class CollateralService(BaseService):
    def __init__(
        self,
        collateral_repository: CollateralRepository,
        transformation_service: TransformationService,
    ):
        self.collateral_repository = collateral_repository
        self.transformation_service = transformation_service

    async def get_collateral_form_by_id(
        self, race_date: str, race_id: int, todays_race_date: str
    ):
        return await self.collateral_repository.get_collateral_form_by_id(
            race_date, race_id, todays_race_date
        )


def get_collateral_service(
    collateral_repository: CollateralRepository = Depends(get_collateral_repository),
):
    transformation_service = TransformationService()
    return CollateralService(collateral_repository, transformation_service)
