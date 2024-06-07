from datetime import datetime, timedelta

import pandas as pd
from fastapi import Depends

from .betfair_service import BetfairService, get_betfair_service

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
    betfair_service: BetfairService

    def __init__(
        self,
        todays_repository: TodaysRepository,
        transformation_service: TransformationService,
        betfair_service: BetfairService,
    ):
        self.todays_repository = todays_repository
        self.transformation_service = transformation_service
        self.betfair_service = betfair_service

    @staticmethod
    def filter_dataframe_by_date(data: pd.DataFrame) -> pd.DataFrame:
        date_filter = (
            datetime.now() - timedelta(weeks=FILTER_PERIOD)
        ).strftime("%Y-%m-%d")
        return data[data["race_time"] > date_filter].copy()

    async def get_market_ids(self, race_id: int):
        d = read_json("./src/cache/market_ids.json")
        return [
            [i["market_id_win"], i["market_id_place"]]
            for i in d
            if i["race_id"] == race_id
        ][0]

    async def get_todays_races(self):
        data = await self.todays_repository.get_todays_races()
        return self.format_todays_races(data)

    async def get_race_by_id(self, date: str, race_id: int):

        market_ids = await self.get_market_ids(race_id)
        betfair_data = await self.betfair_service.get_current_market_data(market_ids)
        todays_data = await self.todays_repository.get_race_by_id(date, race_id)
        betfair_ids = await self.todays_repository.get_todays_betfair_ids()
        data = TodaysService.curate_live_race_data(todays_data, betfair_data, betfair_ids)
        data = data.pipe(TodaysService.filter_dataframe_by_date).pipe(
            self.transformation_service.calculate, date
        )
        data.pipe(
            self.convert_string_columns,
            [
                "headgear",
                "finishing_position",
                "industry_sp",
                "in_race_comment",
                "tf_comment",
                "tfr_view",
                "conditions",
                "going",
                "hcap_range",
                "age_range",
                "surface",
                "winning_time",
                "relative_to_standard",
                "country",
                "main_race_comment",
            ],
        )
        data.pipe(
            self.convert_integer_columns,
            [
                "draw",
                "days_since_last_ran",
                "days_since_performance",
                "extra_weight",
                "jockey_claim",
                "official_rating",
                "ts",
                "rpr",
                "tfr",
                "tfig",
                "race_class",
                "number_of_runners",
                "total_prize_money",
                "first_place_prize_money",
            ],
        )
        data = data.assign(headgear=data["headgear"].replace("None", None))

        today = data[data["data_type"] == "today"]
        historical = data[data["data_type"] == "historical"]

        race_details = today.drop_duplicates(subset=["unique_id"]).to_dict(
            orient="records"
        )[0]

        today = today.rename(
            columns={
                "betfair_win_sp": "todays_betfair_win_sp",
                "betfair_place_sp": "todays_betfair_place_sp",
            }
        )

        historical = historical.merge(
            today[["horse_id", "todays_betfair_win_sp", "todays_betfair_place_sp"]],
            on="horse_id",
        )
        historical = historical.sort_values(
            by=["horse_id", "race_date"], ascending=[True, False]
        )

        grouped = historical.groupby(["horse_id", "horse_name"])

        data = {
            "race_id": race_details["race_id"],
            "course": race_details["course"],
            "distance": race_details["distance"],
            "going": race_details["going"],
            "surface": race_details["surface"],
            "race_class": race_details["race_class"],
            "hcap_range": race_details["hcap_range"],
            "age_range": race_details["age_range"],
            "conditions": race_details["conditions"],
            "race_type": race_details["race_type"],
            "race_title": race_details["race_title"],
            "race_time": race_details["race_time"],
            "race_date": race_details["race_date"],
            "horse_data": [
                {
                    "horse_name": name,
                    "horse_id": horse_id,
                    "first_places": group["first_places"].iloc[0],
                    "second_places": group["second_places"].iloc[0],
                    "third_places": group["third_places"].iloc[0],
                    "fourth_places": group["fourth_places"].iloc[0],
                    "number_of_runs": group["number_of_runs"].iloc[0],
                    "todays_betfair_win_sp": group["todays_betfair_win_sp"].iloc[0],
                    "todays_betfair_place_sp": group["todays_betfair_place_sp"].iloc[0],
                    "performance_data": group.drop(
                        columns=[
                            "horse_id",
                            "horse_name",
                            "first_places",
                            "second_places",
                            "third_places",
                            "fourth_places",
                            "todays_betfair_win_sp",
                            "todays_betfair_place_sp",
                        ]
                    ).to_dict(orient="records"),
                }
                for (horse_id, name), group in grouped
            ],
        }

        print(data)

        return data

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

        return todays_data

    async def get_race_graph_by_id(self, date: str, race_id: int):
        data = await self.todays_repository.get_race_graph_by_id(date, race_id)
        data = data.pipe(TodaysService.filter_dataframe_by_date, date).pipe(
            self.convert_integer_columns,
            [
                "official_rating",
                "ts",
                "rpr",
                "tfr",
                "tfig",
            ],
        )
        performance_data = []
        for horse in data["horse_name"].unique():
            horse_data = data[data["horse_name"] == horse]
            performance_data.append(
                {
                    "horse_name": horse_data["horse_name"].iloc[0],
                    "horse_id": horse_data["horse_id"].iloc[0],
                    "performance_data": horse_data.to_dict(orient="records"),
                }
            )

        return performance_data


def get_todays_service(
    todays_repository: TodaysRepository = Depends(get_todays_repository),
):
    transformation_service = TransformationService()
    betfair_service = get_betfair_service()
    return TodaysService(todays_repository, transformation_service, betfair_service)
