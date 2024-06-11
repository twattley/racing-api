from datetime import datetime, timedelta
import numpy as np

import pandas as pd
from fastapi import Depends

from api_helpers.betfair_client import (
    BetfairCredentials,
    BetfairApiHelper,
    BetFairClient
)

from src.config import config

trading_client = BetFairClient(
    BetfairCredentials(
        username=config.bf_username,
        password=config.bf_password,
        app_key=config.bf_app_key,
        certs_path=config.bf_certs_path,
    )
)
trading_client.login()


from ..repository.todays_repository import TodaysRepository, get_todays_repository
from ..utils.json_utils import read_json, write_json
from .base_service import BaseService
from .transformation_service import TransformationService

FILTER_WEEKS = 52
FILTER_YEARS = 3
FILTER_PERIOD = FILTER_WEEKS * FILTER_YEARS


class TodaysService(BaseService):

    todays_repository: TodaysRepository
    transformation_service: TransformationService
    betfair_service: BetfairApiHelper

    def __init__(
        self,
        todays_repository: TodaysRepository,
        transformation_service: TransformationService,
        betfair_service: BetfairApiHelper,
    ):
        self.todays_repository = todays_repository
        self.transformation_service = transformation_service
        self.betfair_service = betfair_service

    @staticmethod
    def filter_dataframe_by_date(data: pd.DataFrame, date_filter: str) -> pd.DataFrame:
        return data[data["race_time"] > date_filter].copy()

    async def get_market_ids(self, race_id: int):
        d = read_json("./src/cache/market_ids.json")
        for i in d:
            if i['race_id'] == race_id:
                return [i["market_id_win"], i["market_id_place"]]
        raise ValueError(f"No market ids found for race id {race_id}")

    async def get_todays_races(self):
        data = await self.todays_repository.get_todays_races()
        return self.format_todays_races(data[data["race_time"] >= datetime.now()])

    async def get_race_by_id(self, race_id: int):
        date_filter = (datetime.now() - timedelta(weeks=FILTER_PERIOD)).strftime(
            "%Y-%m-%d"
        )
        date = datetime.now().strftime("%Y-%m-%d")
        market_ids = await self.get_market_ids(race_id)
        todays_data = await self.todays_repository.get_race_by_id(date, race_id)
        betfair_ids = await self.todays_repository.get_todays_betfair_ids()
        betfair_data = self.betfair_service.create_single_market_data(market_ids)
        data = TodaysService.curate_live_race_data(
            todays_data, betfair_data, betfair_ids
        )
        return self.format_todays_form_data(
            data,
            date,
            date_filter,
            TodaysService.filter_dataframe_by_date,
            self.transformation_service.calculate,
        )

    @staticmethod
    def curate_live_race_data(todays_data, betfair_data, betfair_ids):
        win_and_place = (
            pd.merge(
                betfair_data[betfair_data["market"] == "WIN"],
                betfair_data[betfair_data["market"] == "PLACE"],
                on=["race_time", "course", "todays_bf_unique_id"],
                suffixes=("_win", "_place"),
            )
            .rename(
                columns={
                    "horse_win": "horse_name",
                    "last_traded_price_win": "betfair_win_sp",
                    "last_traded_price_place": "betfair_place_sp",
                    "status_win": "status",
                    "market_id_win": "market_id_win",
                    "market_id_place": "market_id_place",
                }
            )
            .filter(
                items=[
                    "race_time",
                    "todays_bf_unique_id",
                    "horse_name",
                    "course",
                    "betfair_win_sp",
                    "betfair_place_sp",
                    "status",
                    "market_id_win",
                    "market_id_place",
                ]
            )
            .sort_values(by="race_time", ascending=True)
        ).merge(betfair_ids, on="todays_bf_unique_id", how="left")

        runners = win_and_place[win_and_place['status'] == 'ACTIVE']['horse_id'].unique()

        win_sp = dict(zip(win_and_place["horse_id"], win_and_place["betfair_win_sp"]))
        place_sp = dict(
            zip(win_and_place["horse_id"], win_and_place["betfair_place_sp"])
        )

        todays_data.loc[todays_data["data_type"] == "today", "betfair_win_sp"] = (
            todays_data.loc[todays_data["data_type"] == "today", "horse_id"].map(win_sp)
        )
        todays_data.loc[todays_data["data_type"] == "today", "betfair_place_sp"] = (
            todays_data.loc[todays_data["data_type"] == "today", "horse_id"].map(
                place_sp
            )
        )

        return todays_data[todays_data['horse_id'].isin(runners)]

    async def get_race_graph_by_id(self, race_id: int):
        date_filter = (datetime.now() - timedelta(weeks=FILTER_PERIOD)).strftime(
            "%Y-%m-%d"
        )
        date = datetime.now().strftime("%Y-%m-%d")
        data = await self.todays_repository.get_race_graph_by_id(date, race_id)
        return self.format_todays_graph_data(
            data,
            date_filter,
            TodaysService.filter_dataframe_by_date,
        )
        

def get_todays_service(
    todays_repository: TodaysRepository = Depends(get_todays_repository),
):
    transformation_service = TransformationService()
    betfair_service = BetfairApiHelper(trading_client)
    return TodaysService(todays_repository, transformation_service, betfair_service)
