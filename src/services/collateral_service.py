import numpy as np
import pandas as pd
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
        self, race_date: str, race_id: int, todays_race_date: str, horse_id: int
    ):
        data = await self.collateral_repository.get_collateral_form_by_id(
            race_date, race_id, todays_race_date, horse_id
        )
        transformed_data = self.transformation_service.transform_collateral_form_data(
            data
        )

        transformed_data = transformed_data.pipe(
            self.convert_string_columns,
            [
                "headgear",
                "weight_carried",
                "finishing_position",
                "tf_comment",
                "tfr_view",
            ],
        )
        transformed_data = transformed_data.pipe(
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

        transformed_data["official_rating"] = transformed_data[
            "official_rating"
        ].fillna(0)

        transformed_data = transformed_data.sort_values(
            by=["distance_difference", "horse_id"], ascending=[True, False]
        ).reset_index(drop=True)

        horse_collateral_data = []
        all_valid_ratings = []
        number_of_runs = []
        all_important_results = []

        for horse in transformed_data["horse_name"].unique():
            horse_data = transformed_data[transformed_data["horse_name"] == horse]
            race_form = horse_data[horse_data["data_type"] == "race_form"]
            collateral = horse_data[horse_data["data_type"] == "collateral"]

            if collateral.empty:
                continue

            valid_ratings = collateral[collateral["rating"] > 30]["rating"]
            all_valid_ratings.extend(valid_ratings)
            number_of_runs.extend(collateral["rating"])

            important_results = (
                (collateral["finishing_position"].isin(["1", "2"]))
                | (collateral["total_distance_beaten"].astype(float) < 2)
                | (
                    (collateral["finishing_position"].isin(["1", "2", "3"]))
                    & (collateral["number_of_runners"].astype(int) >= 12)
                )
                | (
                    (collateral["finishing_position"].isin(["1", "2", "3", "4"]))
                    & (collateral["number_of_runners"].astype(int) >= 16)
                )
            )

            all_important_results.append(important_results)
            horse_data = {
                "horse_id": race_form["horse_id"].iloc[0],
                "horse_name": race_form["horse_name"].iloc[0],
                "distance_difference": race_form["distance_difference"].iloc[0],
                "betfair_win_sp": race_form["betfair_win_sp"].iloc[0],
                "official_rating": race_form["official_rating"].iloc[0],
                "collateral_form_data": [],
            }

            for _, row in collateral.iterrows():
                collateral_form = {
                    "official_rating": row["official_rating"],
                    "finishing_position": row["finishing_position"],
                    "total_distance_beaten": row["total_distance_beaten"],
                    "betfair_win_sp": row["betfair_win_sp"],
                    "rating": row["rating"],
                    "speed_figure": row["speed_figure"],
                    "horse_id": row["horse_id"],
                    "unique_id": row["unique_id"],
                    "race_id": row["race_id"],
                    "race_time": row["race_time"],
                    "race_date": row["race_date"],
                    "race_type": row["race_type"],
                    "race_class": row["race_class"],
                    "distance": row["distance"],
                    "conditions": row["conditions"],
                    "going": row["going"],
                    "number_of_runners": row["number_of_runners"],
                    "surface": row["surface"],
                    "main_race_comment": row["main_race_comment"],
                    "tf_comment": row["tf_comment"],
                    "tfr_view": row["tfr_view"],
                }
                horse_data["collateral_form_data"].append(collateral_form)

            horse_collateral_data.append(horse_data)

        important_result_count = np.sum(
            [results.sum() for results in all_important_results]
        )

        average_rating = (
            round(pd.Series(all_valid_ratings).mean()) if all_valid_ratings else 0
        )
        valid_performance_count = len(number_of_runs)

        response = {
            "average_collateral_rating": average_rating,
            "valid_collateral_performance_count": valid_performance_count,
            "important_result_count": int(important_result_count),
            "horse_collateral_data": horse_collateral_data,
        }
        return self.sanitize_nan(response)


def get_collateral_service(
    collateral_repository: CollateralRepository = Depends(get_collateral_repository),
):
    transformation_service = TransformationService()
    return CollateralService(collateral_repository, transformation_service)
