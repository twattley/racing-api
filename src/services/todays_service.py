from datetime import datetime

from fastapi import Depends

from ..repository.todays_repository import TodaysRepository, get_todays_repository
from .base_service import BaseService
from .prices_service import PricesService, get_prices_service
from .transformation_service import TransformationService
import pandas as pd


class TodaysService(BaseService):
    todays_repository: TodaysRepository
    transformation_service: TransformationService
    prices_service: PricesService

    def __init__(
        self,
        todays_repository: TodaysRepository,
        transformation_service: TransformationService,
        prices_service: PricesService,
    ):
        self.todays_repository = todays_repository
        self.transformation_service = transformation_service
        self.prices_service = prices_service

    async def get_todays_races(self):
        data = await self.todays_repository.get_todays_races()
        return self.format_todays_races(data[data["race_time"] >= datetime.now()])

    async def get_race_by_id(self, race_id: int):
        todays_data = await self.todays_repository.get_race_by_id(race_id)
        prices = await self.prices_service.get_current_prices()
        data = self._merge_prices_with_data(todays_data, prices)
        return self.format_todays_form_data(
            data,
            self.transformation_service.calculate,
        )

    def _merge_prices_with_data(
        self, data: pd.DataFrame, prices: pd.DataFrame
    ) -> pd.DataFrame:
        today = data[data["data_type"] == "today"]
        hist = data[~(data["data_type"] == "today")].assign(betfair_id=None)

        prices = prices.rename(columns={"horse_id": "betfair_id"})

        today = (
            today.merge(prices, left_on="betfair_id", right_on="betfair_id", how="left")
            .drop(
                columns=[
                    "betfair_win_sp_x",
                    "betfair_place_sp_x",
                    "market_id_win",
                    "market_id_place",
                    "price_change_x",
                ]
            )
            .rename(
                columns={
                    "betfair_win_sp_y": "betfair_win_sp",
                    "betfair_place_sp_y": "betfair_place_sp",
                    "price_change_y": "price_change",
                }
            )
        )

        data = pd.concat([hist, today]).reset_index(drop=True)
        return data


def get_todays_service(
    todays_repository: TodaysRepository = Depends(get_todays_repository),
    prices_service: PricesService = Depends(get_prices_service),
):
    transformation_service = TransformationService()
    return TodaysService(todays_repository, transformation_service, prices_service)
