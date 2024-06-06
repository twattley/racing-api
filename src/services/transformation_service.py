import numpy as np
import pandas as pd


class TransformationService:
    def __init__(self):
        pass

    def _sort_data(self, data: pd.DataFrame) -> pd.DataFrame:
        return data.sort_values(by=["horse_id", "race_date"])

    def _create_tmp_vars(self, data: pd.DataFrame, date: str) -> pd.DataFrame:
        return data.assign(
            race_date_tmp=pd.to_datetime(data["race_date"], errors="coerce"),
            todays_date_tmp=pd.to_datetime(date, errors="coerce"),
        )

    def _create_days_since_last_ran(self, data: pd.DataFrame) -> pd.DataFrame:
        return data.assign(
            days_since_last_ran=data.sort_values("race_date_tmp")
            .groupby("horse_id")["race_date_tmp"]
            .diff()
            .dt.days.astype("Int64")
        )

    def _create_number_of_runs(self, data: pd.DataFrame) -> pd.DataFrame:
        return data.assign(
            number_of_runs=data.groupby("horse_id")["race_time"].transform(
                lambda x: x.rank(method="first").shift(1, fill_value=0).astype("Int64")
            )
        )

    def _create_days_since_performance(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.assign(
            days_since_performance=(
                data["todays_date_tmp"] - data["race_date_tmp"]
            ).dt.days
        )
        return data

    def _calculate_places(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.assign(
            first_places=((data["finishing_position"] == "1"))
            .groupby(data["horse_id"])
            .cumsum()
            .shift(1, fill_value="0"),
            second_places=((data["finishing_position"] == "2"))
            .groupby(data["horse_id"])
            .cumsum()
            .shift(1, fill_value="0"),
            third_places=(
                (data["finishing_position"] == "3") & (data["number_of_runners"] > 7)
            )
            .groupby(data["horse_id"])
            .cumsum()
            .shift(1, fill_value="0"),
            fourth_places=(
                (data["finishing_position"] == "4") & (data["number_of_runners"] > 12)
            )
            .groupby(data["horse_id"])
            .cumsum()
            .shift(1, fill_value="0"),
        )

        return data

    def _create_distance_diff(self, data: pd.DataFrame) -> pd.DataFrame:
        todays_distance = data[data["data_type"] == "today"]["distance_meters"].iloc[0]
        return data.assign(
            distance_diff=(data["distance_meters"] - todays_distance).round(-2)
        )

    def _cleanup_temp_vars(self, data: pd.DataFrame) -> pd.DataFrame:
        return data.drop(columns=["race_date_tmp", "todays_date_tmp"])

    def calculate(self, data: pd.DataFrame, date: str) -> pd.DataFrame:

        return (
            self._create_tmp_vars(data, date)
            .pipe(self._sort_data)
            .pipe(self._create_days_since_performance)
            .pipe(self._create_days_since_last_ran)
            .pipe(self._create_number_of_runs)
            .pipe(self._calculate_places)
            .pipe(self._create_distance_diff)
            .pipe(self._cleanup_temp_vars)
        )

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
