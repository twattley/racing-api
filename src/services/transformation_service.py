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
        data = data.assign(
            days_since_last_ran=data.sort_values("race_date_tmp")
            .groupby("horse_id")["race_date_tmp"]
            .diff()
            .dt.days.astype("Int64")
        )

        return data.assign(weeks_since_last_ran=data["days_since_last_ran"] // 7)

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
        return data.assign(weeks_since_performance=data["days_since_performance"] // 7)

    @staticmethod
    def _calculate_combined_ratings(data: pd.DataFrame) -> pd.DataFrame:
        return data.assign(
            rating=lambda data: ((data["tfr"] + data["rpr"]) / 2).fillna(0).astype(int),
            speed_figure=lambda data: ((data["ts"] + data["tfig"]) / 2)
            .fillna(0)
            .astype(int),
        )

    @staticmethod
    def _calculate_rating_diffs(data: pd.DataFrame) -> pd.DataFrame:
        return data.assign(
            rating_diff=(data["rating"] - data["median_rating"])
            .round(0)
            .fillna(0)
            .astype(int),
            speed_rating_diff=(data["speed_figure"] - data["median_speed"])
            .round(0)
            .fillna(0)
            .astype(int),
        )

    @staticmethod
    def _round_price_data(data: pd.DataFrame) -> pd.DataFrame:
        def custom_round(x):
            if x is None:
                return None
            if abs(x) >= 10:
                return round(x)
            else:
                return round(x, 1)

        return data.assign(
            betfair_win_sp=data["betfair_win_sp"].apply(custom_round),
            betfair_place_sp=data["betfair_place_sp"].apply(custom_round),
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
        todays_distance = data[data["data_type"] == "today"]["distance_yards"].iloc[0]
        return data.assign(
            distance_diff=(data["distance_yards"] - todays_distance).round(-2)
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

    @staticmethod
    def _create_todays_rating(data: pd.DataFrame) -> pd.DataFrame:
        data["rank"] = data.groupby("horse_id")["race_date"].rank(
            ascending=False, method="dense"
        )
        data["race_time"] = pd.to_datetime(data["race_time"])
        today = pd.to_datetime(data[data["data_type"] == "today"]["race_date"].iloc[0])
        two_years_ago = today - pd.DateOffset(years=2)
        filtered_data = data[
            (data["race_time"] >= two_years_ago)
            & (data["rank"] <= 5)
            & (data["speed_figure"] >= 15)
            & (data["rating"] >= 15)
        ]

        medians = filtered_data.groupby("horse_id")[["speed_figure", "rating"]].median()
        medians.columns = ["median_speed", "median_rating"]
        means = filtered_data.groupby("horse_id")[["speed_figure", "rating"]].mean()
        means.columns = ["mean_speed", "mean_rating"]

        medians = medians.rename(
            columns={"speed_figure": "median_speed", "rating": "median_rating"}
        )
        means = means.rename(
            columns={"speed_figure": "mean_speed", "rating": "mean_rating"}
        )
        result = data.merge(medians, on="horse_id", how="left")
        result = result.merge(means, on="horse_id", how="left")

        return result

    @staticmethod
    def _fill_todays_rating(data: pd.DataFrame) -> pd.DataFrame:
        data["rating_tmp"] = (data["median_rating"] + data["mean_rating"]) / 2
        data["speed_rating_tmp"] = (data["median_speed"] + data["mean_speed"]) / 2
        data["speed_figure"] = np.where(
            data["data_type"] == "today",
            data["speed_rating_tmp"],
            data["speed_figure"],
        )
        data["rating"] = np.where(
            data["data_type"] == "today",
            data["rating_tmp"],
            data["rating"],
        )
        data = data.drop(
            columns=[
                "rating_tmp",
                "speed_rating_tmp",
                "mean_rating",
                "mean_speed",
            ]
        )
        data["rating"] = data["rating"].round(0).astype(int)
        data["speed_figure"] = data["speed_figure"].round(0).astype(int)

        return data

    @staticmethod
    def _set_figure_visibility(data: pd.DataFrame) -> pd.DataFrame:
        data = data.sort_values(by=["race_time"])
        data["running_max"] = data["rating"].cummax()
        data["within_5"] = data["rating"] >= (data["running_max"] - 5)
        horses_within_5 = data.groupby("horse_name")["within_5"].transform("any")
        data["figure_visibility"] = horses_within_5

        return data.drop(columns=["running_max", "within_5"])

    @staticmethod
    def _set_variance_visibility(data: pd.DataFrame) -> pd.DataFrame:
        def calculate_cv_with_exclusions(group):
            num_runs = len(group)
            if num_runs > 1:
                mean = group["rating"].mean()
                std = group["rating"].std()
                poor_performance = group["rating"] < (mean - std)

                if num_runs <= 8:
                    num_exclusions = 1
                else:
                    num_exclusions = 2

                for _ in range(num_exclusions):
                    if poor_performance.any():
                        index_to_exclude = poor_performance.idxmax()
                        group = group.drop(index_to_exclude)
                        poor_performance = group["rating"] < (
                            group["rating"].mean() - group["rating"].std()
                        )

                mean = group["rating"].mean()
                std = group["rating"].std()

            cv = std / mean if mean != 0 else float("inf")
            return cv

        cv_values = data.groupby("horse_name", group_keys=False).apply(
            calculate_cv_with_exclusions
        )

        variance_visibility = cv_values <= 0.3

        data["variance_visibility"] = data["horse_name"].map(variance_visibility)

        return data

    @staticmethod
    def calculate(data: pd.DataFrame, date: str) -> pd.DataFrame:
        data = (
            TransformationService._create_tmp_vars(data, date)
            .pipe(TransformationService._sort_data)
            .pipe(TransformationService._create_days_since_performance)
            .pipe(TransformationService._create_days_since_last_ran)
            .pipe(TransformationService._create_number_of_runs)
            .pipe(TransformationService._calculate_places)
            .pipe(TransformationService._create_distance_diff)
            .pipe(TransformationService._calculate_combined_ratings)
            .pipe(TransformationService._create_todays_rating)
            .pipe(TransformationService._fill_todays_rating)
            .pipe(TransformationService._calculate_rating_diffs)
            .pipe(TransformationService._round_price_data)
            .pipe(TransformationService._cleanup_temp_vars)
            .pipe(TransformationService._set_figure_visibility)
            .pipe(TransformationService._set_variance_visibility)
        )

        return data
