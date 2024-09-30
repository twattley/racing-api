import json

import numpy as np
import pandas as pd
from fastapi import Depends

from src.models.betting_selections import BettingSelections

from ..repository.betting_repository import BettingRepository, get_betting_repository
from .base_service import BaseService


class BettingService(BaseService):
    def __init__(
        self,
        betting_repository: BettingRepository,
    ):
        self.betting_repository = betting_repository
        self._get_betting_session_id()

    def _get_betting_session_id(self):
        with open("betting_session.json", "r") as f:
            session_id = json.load(f)["session_id"]
            self.betting_session_id = int(session_id) + 1

    async def store_betting_selections(self, selections: BettingSelections):
        await self.betting_repository.store_betting_selections(
            selections, self.betting_session_id
        )

    async def get_betting_selections_analysis(self):
        data = await self.betting_repository.get_betting_selections_analysis()
        data = data.pipe(self._calculate_dutch_sum)
        return data

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
                    "calculated_odds": lambda x: (
                        x.max() if "dutch" in x.name.lower() else x.iloc[0]
                    ),
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
        result["bet_result"] = result["bet_result"].astype(float)
        result = result.sort_values(["betting_type", "created_at"])

        result["official_rating"] = result["official_rating"].fillna(0).astype(int)

        self.convert_integer_columns(
            result,
            [
                "official_rating",
                "ts",
                "rpr",
                "tfr",
                "tfig",
            ],
        )
        # First, separate dutch and non-dutch bets
        dutch_bets = result[result["betting_type"].str.contains("dutch", case=False)]
        non_dutch_bets = result[
            ~result["betting_type"].str.contains("dutch", case=False)
        ]

        # Drop duplicates for dutch bets
        dutch_bets_deduplicated = dutch_bets.drop_duplicates(
            subset=["race_id"], keep="first"
        )

        result = pd.concat([dutch_bets_deduplicated, non_dutch_bets]).sort_index()
        result["bet_number"] = result.groupby("betting_type").cumcount() + 1
        result["running_total"] = result.groupby("betting_type")["bet_result"].cumsum()
        result["overall_total"] = result["bet_result"].cumsum()
        overall_total = result["overall_total"].iloc[-1]
        number_of_bets = len(result)
        session_results = result[result["session_id"] == self.betting_session_id]
        session_results["overall_total"] = session_results["bet_result"].cumsum()
        if len(session_results) > 0:
            session_overall_total = session_results["overall_total"].iloc[-1]
            session_number_of_bets = len(session_results)
        else:
            session_overall_total = 0
            session_number_of_bets = 0

        result = result.sort_values(["betting_type", "created_at"])
        result_dict = self.sanitize_nan(result.to_dict(orient="records"))

        return {
            "number_of_bets": number_of_bets,
            "overall_total": overall_total,
            "session_number_of_bets": session_number_of_bets,
            "session_overall_total": session_overall_total,
            "result_dict": result_dict,
        }


def get_betting_service(
    betting_repository: BettingRepository = Depends(get_betting_repository),
):
    return BettingService(betting_repository)
