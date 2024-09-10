from fastapi import Depends

from ..repository.feedback_repository import FeedbackRepository, get_feedback_repository
from .base_service import BaseService
from .transformation_service import TransformationService


class FeedbackService(BaseService):
    def __init__(
        self,
        feedback_repository: FeedbackRepository,
        transformation_service: TransformationService,
    ):
        self.feedback_repository = feedback_repository
        self.transformation_service = transformation_service

    async def get_todays_races(self):
        data = await self.feedback_repository.get_todays_races()
        return self.format_todays_races(data)

    async def get_race_by_id(self, race_id: int):
        data = await self.feedback_repository.get_race_by_id(race_id)
        return self.format_todays_form_data(
            data,
            self.transformation_service.calculate,
        )

    async def get_race_result_by_id(self, race_id: int):
        data = await self.feedback_repository.get_race_result_by_id(race_id)
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

    async def get_current_date_today(self):
        data = await self.feedback_repository.get_current_date_today()
        return data

    async def store_current_date_today(self, date: str):
        await self.feedback_repository.store_current_date_today(date)


def get_feedback_service(
    feedback_repository: FeedbackRepository = Depends(get_feedback_repository),
):
    transformation_service = TransformationService()
    return FeedbackService(feedback_repository, transformation_service)
