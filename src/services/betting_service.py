from fastapi import Depends
import pandas as pd
import numpy as np

from src.models.betting_selections import BettingSelections

from ..repository.betting_repository import (
    BettingRepository,
    get_betting_repository,
)
from .base_service import BaseService


class BettingService(BaseService):
    def __init__(
        self,
        betting_repository: BettingRepository,
    ):
        self.betting_repository = betting_repository

    async def store_betting_selections(self, selections: BettingSelections):
        await self.betting_repository.store_betting_selections(selections)

    async def get_betting_selections_analysis(self):
        data = await self.betting_repository.get_betting_selections_analysis()
        print(data.info())
        return data.pipe(self._calculate_dutch_sum)

    def _calculate_dutch_sum(self, data: pd.DataFrame) -> pd.DataFrame:
        data["betfair_win_sp"] = data["betfair_win_sp"].astype(float)
        data["dutch_sum"] = (
            data[data["betting_type"].str.contains("dutch", case=False)]
            .groupby(["race_id", "betting_type"])["betfair_win_sp"]
            .transform(lambda x: (100.0 / x).sum())
        )

        data["calculated_odds"] = np.where(
            data["betting_type"].str.contains("dutch", case=False),
            100.0 / data["dutch_sum"],
            data["betfair_win_sp"].round(2),
        )

        grouped = (
            data.groupby(["race_id", "betting_type"])
            .agg(
                {
                    "calculated_odds": lambda x: x.max()
                    if "dutch" in x.name.lower()
                    else x.iloc[0],
                    "betfair_win_sp": "first",
                }
            )
            .round(2)
            .reset_index()
        )
        grouped.columns = ["race_id", "betting_type", "final_odds", "betfair_win_sp"]

        result = data.merge(
            grouped, on=["race_id", "betting_type"], suffixes=("", "_grouped")
        )

        result["adjusted_final_odds"] = np.select(
            [
                result["betting_type"].str.contains("lay", case=False),
                result["betting_type"].str.contains("back", case=False),
            ],
            [result["final_odds"] * 1.15, result["final_odds"] * 0.85],
            default=result["final_odds"],
        ).round(2)

        result["win"] = result["finishing_position"] == "1"
        result["place"] = (
            (result["number_of_runners"] < 8)
            & (result["finishing_position"].isin(["1", "2"]))
        ) | (
            (result["number_of_runners"] >= 8)
            & (result["finishing_position"].isin(["1", "2", "3"]))
        )

        conditions = [
            (result["betting_type"] == "back_mid_price")
            & (result["finishing_position"] == "1"),
            (result["betting_type"] == "back_mid_price")
            & (result["finishing_position"] != "1"),
            (result["betting_type"] == "back_outsider")
            & (result["finishing_position"] == "1"),
            (result["betting_type"] == "back_outsider")
            & (result["finishing_position"] != "1"),
            (result["betting_type"] == "back_outsider_place") & result["place"],
            (result["betting_type"] == "back_outsider_place") & ~result["place"],
            (result["betting_type"] == "lay_favourite")
            & (result["finishing_position"] == "1"),
            (result["betting_type"] == "lay_favourite")
            & (result["finishing_position"] != "1"),
            (result["betting_type"] == "lay_mid_price_place") & result["place"],
            (result["betting_type"] == "lay_mid_price_place") & ~result["place"],
            (result["betting_type"] == "dutch_back")
            & (result["finishing_position"] == "1"),
            (result["betting_type"] == "dutch_back")
            & (result["finishing_position"] != "1"),
            (result["betting_type"] == "dutch_lay")
            & (result["finishing_position"] == "1"),
            (result["betting_type"] == "dutch_lay")
            & (result["finishing_position"] != "1"),
        ]

        choices = [
            (result["final_odds"] * 0.85 - 1).round(2),
            -1,
            (result["final_odds"] * 0.85 - 1).round(2),
            -1,
            (result["betfair_place_sp"] - 1).round(2),
            -1,
            (-(result["final_odds"] * 1.15 - 1)).round(2),
            0.9,
            (-(result["betfair_place_sp"] - 1)).round(2),
            0.9,
            (result["final_odds"] * 0.85 - 1).round(2),
            -1,
            (-(result["final_odds"] * 1.15 - 1)).round(2),
            0.9,
        ]

        result["bet_result"] = np.select(conditions, choices, default=0)

        dutch_back_results = (
            result[result["betting_type"] == "dutch_back"]
            .groupby("race_id")["bet_result"]
            .transform("max")
        )
        dutch_lay_results = (
            result[result["betting_type"] == "dutch_lay"]
            .groupby("race_id")["bet_result"]
            .transform("min")
        )

        result.loc[result["betting_type"] == "dutch_back", "bet_result"] = (
            dutch_back_results
        )
        result.loc[result["betting_type"] == "dutch_lay", "bet_result"] = (
            dutch_lay_results
        )
        result = result.sort_values(["race_id", "betting_type"])

        self.convert_integer_columns(
            result,
            [
                "official_rating",
                "ts",
                "rpr",
                "tfr",
                "tfig",
                "in_play_high",
                "in_play_low",
            ],
        )

        result_dict = result.drop_duplicates(
            subset=["race_id", "dutch_sum"], keep="first"
        ).to_dict(orient="records")

        return self.sanitize_nan(result_dict)


def get_betting_service(
    betting_repository: BettingRepository = Depends(get_betting_repository),
):
    return BettingService(betting_repository)
