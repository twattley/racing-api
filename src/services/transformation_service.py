import numpy as np
import pandas as pd


class TransformationService:
    def __init__(self):
        pass

    @staticmethod
    def _sort_data(data: pd.DataFrame) -> pd.DataFrame:
        return data.sort_values(by=["horse_id", "race_date"])

    @staticmethod
    def _create_tmp_vars(data: pd.DataFrame, date: str) -> pd.DataFrame:
        return data.assign(
            race_date_tmp=pd.to_datetime(data["race_date"], errors="coerce"),
            todays_date_tmp=pd.to_datetime(date, errors="coerce"),
        )

    @staticmethod
    def _create_days_since_last_ran(data: pd.DataFrame) -> pd.DataFrame:
        return data.assign(
            days_since_last_ran=data.sort_values("race_date_tmp")
            .groupby("horse_id")["race_date_tmp"]
            .diff()
            .dt.days.astype("Int64")
        )

    @staticmethod
    def _create_number_of_runs(data: pd.DataFrame) -> pd.DataFrame:
        return data.assign(
            number_of_runs=data.groupby("horse_id")["race_time"].transform(
                lambda x: x.rank(method="first").astype("Int64")
            )
        )

    @staticmethod
    def _create_days_since_performance(data: pd.DataFrame) -> pd.DataFrame:
        data = data.assign(
            days_since_performance=(
                data["todays_date_tmp"] - data["race_date_tmp"]
            ).dt.days
        )
        return data

    @staticmethod
    def _calculate_combined_ratings(data: pd.DataFrame) -> pd.DataFrame:
        return data.assign(
            rating=lambda data: ((data["tfr"] + data["rpr"]) / 2).fillna(0).astype(int),
            speed_figure=lambda data: ((data["ts"] + data["tfig"]) / 2)
            .fillna(0)
            .astype(int),
        )

    @staticmethod
    def _calculate_rating_versus_official_rating(data: pd.DataFrame) -> pd.DataFrame:
        return data.assign(
            rating_diff=np.select(
                [
                    data["official_rating"] == 0,
                    data["official_rating"] > 0,
                ],
                [0, data["rating"] - data["official_rating"]],
                default=0,
            ),
            speed_rating_diff=np.select(
                [
                    data["official_rating"] == 0,
                    data["official_rating"] > 0,
                ],
                [0, data["speed_figure"] - data["official_rating"]],
                default=0,
            ),
        )

    @staticmethod
    def _calculate_places(data: pd.DataFrame) -> pd.DataFrame:
        data = data.sort_values(by=["horse_id", "race_time"])
        data["shifted_finishing_position"] = data.groupby("horse_id")[
            "finishing_position"
        ].shift(1, fill_value="0")

        data = data.assign(
            first_places=(data["shifted_finishing_position"] == "1")
            .groupby(data["horse_id"])
            .cumsum(),
            second_places=(data["shifted_finishing_position"] == "2")
            .groupby(data["horse_id"])
            .cumsum(),
            third_places=(
                (data["shifted_finishing_position"] == "3")
                & (data["number_of_runners"] > 7)
            )
            .groupby(data["horse_id"])
            .cumsum(),
            fourth_places=(
                (data["shifted_finishing_position"] == "4")
                & (data["number_of_runners"] > 12)
            )
            .groupby(data["horse_id"])
            .cumsum(),
        )
        data.drop(columns=["shifted_finishing_position"], inplace=True)

        return data

    @staticmethod
    def _create_distance_diff(data: pd.DataFrame) -> pd.DataFrame:
        todays_distance = data[data["data_type"] == "today"]["distance_meters"].iloc[0]
        return data.assign(
            distance_diff=(data["distance_meters"] - todays_distance).round(-2)
        )

    @staticmethod
    def _cleanup_temp_vars(data: pd.DataFrame) -> pd.DataFrame:
        return data.drop(columns=["race_date_tmp", "todays_date_tmp"])

    def amend_finishing_position(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.assign(
            finishing_position_numeric=pd.to_numeric(
                data["finishing_position"], errors="coerce"
            )
        )
        second_place_distance = data[data["finishing_position_numeric"] == 2][
            "total_distance_beaten"
        ].iloc[0]

        data = data.assign(
            total_distance_beaten=np.where(
                pd.isnull(data["finishing_position_numeric"]),
                999.0,
                data["total_distance_beaten"],
            )
        )
        data = data.assign(
            total_distance_beaten=np.where(
                data["finishing_position_numeric"] == 1,
                -second_place_distance,
                data["total_distance_beaten"],
            )
        ).drop(columns=["finishing_position_numeric"])
        return data.sort_values(by=["total_distance_beaten"])

    def calculate(self, data: pd.DataFrame, date: str) -> pd.DataFrame:
        data = (
            TransformationService._create_tmp_vars(data, date)
            .pipe(TransformationService._sort_data)
            .pipe(TransformationService._create_days_since_performance)
            .pipe(TransformationService._create_days_since_last_ran)
            .pipe(TransformationService._create_number_of_runs)
            .pipe(TransformationService._calculate_places)
            .pipe(TransformationService._create_distance_diff)
            .pipe(TransformationService._calculate_combined_ratings)
            .pipe(TransformationService._calculate_rating_versus_official_rating)
            .pipe(TransformationService._cleanup_temp_vars)
        )

        return data
