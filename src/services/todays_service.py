from datetime import datetime, timedelta

import pandas as pd
from fastapi import Depends

from .betfair_service import BetfairService

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
        date_filter = datetime.now() - timedelta(
            weeks=FILTER_PERIOD
        ).strftime("%Y-%m-%d")
        return data[data["race_time"] > date_filter].copy()

    async def get_todays_races(self):
        data = await self.todays_repository.get_todays_races()
        return self.format_todays_races(data)

    async def get_race_by_id(self, date: str, race_id: int):
        todays_data = await self.todays_repository.get_race_by_id(date, race_id)
        betfair_data = await self.betfair_service.get_current_market_data()
        betfair_ids = await self.todays_repository.get_todays_betfair_ids()
        data = self.curate_live_race_data(todays_data, betfair_data, betfair_ids)
        data = data.pipe(TodaysService.filter_dataframe_by_date, date).pipe(
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

        return data

    async def get_race_result_by_id(self, date: str, race_id: int):
        data = await self.feedback_repository.get_race_result_by_id(date, race_id)
        data = data.pipe(self.transformation_service.amend_finishing_position)
        data = data.pipe(
            self.convert_string_columns,
            [
                "headgear",
                "weight_carried",
                "finishing_position",
                "tf_comment",
                "tfr_view",
            ],
        )
        data = data.pipe(
            self.convert_integer_columns,
            [
                "draw",
                "official_rating",
                "ts",
                "rpr",
                "tfr",
                "tfig",
            ],
        )
        race_data = (
            data[
                [
                    "race_time",
                    "race_date",
                    "race_title",
                    "race_type",
                    "race_class",
                    "distance",
                    "conditions",
                    "going",
                    "number_of_runners",
                    "hcap_range",
                    "age_range",
                    "surface",
                    "total_prize_money",
                    "winning_time",
                    "relative_time",
                    "relative_to_standard",
                    "main_race_comment",
                    "course_id",
                    "course",
                    "race_id",
                ]
            ]
            .drop_duplicates(subset=["race_id"])
            .to_dict(orient="records")[0]
        )
        horse_data_list = data[
            [
                "horse_name",
                "horse_id",
                "age",
                "draw",
                "headgear",
                "weight_carried",
                "finishing_position",
                "total_distance_beaten",
                "betfair_win_sp",
                "official_rating",
                "ts",
                "rpr",
                "tfr",
                "tfig",
                "in_play_high",
                "in_play_low",
                "tf_comment",
                "tfr_view",
            ]
        ].to_dict(orient="records")
        race_data["race_results"] = horse_data_list
        return [race_data]

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

    async def get_current_date_today(self) -> list[dict]:
        return read_json("./src/cache/feedback_date.json")

    async def store_current_date_today(self, date: str):
        write_json({"today_date": date}, "./src/cache/feedback_date.json")
        return read_json("./src/cache/feedback_date.json")


def get_todays_service(
    todays_repository: TodaysRepository = Depends(get_todays_repository),
):
    transformation_service = TransformationService()
    return TodaysService(todays_repository, transformation_service)
