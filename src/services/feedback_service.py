from fastapi import Depends
from .transformation_service import TransformationService
from .base_service import BaseService
from ..repository.feedback_repository import (
    FeedbackRepository,
    get_feedback_repository,
)


class FeedbackService(BaseService):
    def __init__(
        self,
        feedback_repository: FeedbackRepository,
        transformation_service: TransformationService,
    ):
        self.feedback_repository = feedback_repository
        self.transformation_service = transformation_service

    async def get_todays_races(self, date: str):
        data = await self.feedback_repository.get_todays_races(date)
        return self.format_todays_races(data)

    async def get_race_by_id(self, date: str, race_id: int):
        data = await self.feedback_repository.get_race_by_id(date, race_id)
        data = data.pipe(self.transformation_service.calculate, date)
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

        grouped = data.groupby(["horse_id", "horse_name"])
        return [
            {
                "horse_name": name,
                "horse_id": horse_id,
                "list": group.drop(columns=["horse_id", "horse_name"]).to_dict(
                    orient="records"
                ),
            }
            for (horse_id, name), group in grouped
        ]

    async def get_race_result_by_id(self, date: str, race_id: int):
        data = await self.feedback_repository.get_race_result_by_id(date, race_id)
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


def get_feedback_service(
    feedback_repository: FeedbackRepository = Depends(get_feedback_repository),
):
    transformation_service = TransformationService()
    return FeedbackService(feedback_repository, transformation_service)
