from typing import Callable

import numpy as np
import pandas as pd


class BaseService:
    def __init__(self):
        pass

    def data_to_dict(self, data: pd.DataFrame) -> list[dict]:
        return [
            {k: v if pd.notna(v) else None for k, v in d.items()}
            for d in data.to_dict(orient="records")
        ]

    def format_todays_races(self, data: pd.DataFrame) -> list[dict]:
        data = data.assign(
            race_class=data["race_class"].fillna(0).astype(int).replace(0, None)
        )
        grouped = data.groupby("course_id")
        courses = []

        for course_id, group in grouped:
            races = group.to_dict(orient="records")
            course_info = {
                "course": group["course"].iloc[0],
                "course_id": course_id,
                "races": races,
            }
            courses.append(course_info)

        return [
            {
                "race_date": data["race_date"].iloc[0],
                "courses": courses,
            }
        ]

    def convert_string_columns(
        self, data: pd.DataFrame, columns: list[str]
    ) -> pd.DataFrame:
        for column in columns:
            data[column] = data[column].astype(str)
        return data

    def convert_integer_columns(
        self, data: pd.DataFrame, columns: list[str]
    ) -> pd.DataFrame:
        for column in columns:
            data[column] = data[column].astype("Int64")
        return data

    def format_todays_form_data(
        self,
        data: pd.DataFrame,
        date: str,
        date_filter: str,
        filter_function: Callable,
        transformation_function: Callable,
    ) -> list[dict]:
        data = data.pipe(filter_function, date_filter).pipe(
            transformation_function, date
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
        data = data.assign(
            headgear=data["headgear"].replace("None", None),
            official_rating=data["official_rating"].fillna(0).astype("Int64"),
        )

        today = data[data["data_type"] == "today"]
        historical = data[data["data_type"] == "historical"]

        race_details = today.drop_duplicates(subset=["unique_id"]).to_dict(
            orient="records"
        )[0]

        today = today.rename(
            columns={
                "betfair_win_sp": "todays_betfair_win_sp",
                "betfair_place_sp": "todays_betfair_place_sp",
                "official_rating": "todays_official_rating",
                "age": "todays_horse_age",
                "days_since_last_ran": "todays_days_since_last_ran",
                "first_places": "todays_first_places",
                "second_places": "todays_second_places",
                "third_places": "todays_third_places",
                "fourth_places": "todays_fourth_places",
            }
        )

        historical = historical.merge(
            today[
                [
                    "horse_id",
                    "todays_betfair_win_sp",
                    "todays_betfair_place_sp",
                    "todays_official_rating",
                    "todays_horse_age",
                    "todays_days_since_last_ran",
                    "todays_first_places",
                    "todays_second_places",
                    "todays_third_places",
                    "todays_fourth_places",
                ]
            ],
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
                    "initial_visibility": group["initial_visibility"].iloc[0],
                    "todays_horse_age": group["todays_horse_age"].iloc[0],
                    "todays_first_places": group["todays_first_places"].iloc[0],
                    "todays_second_places": group["todays_second_places"].iloc[0],
                    "todays_third_places": group["todays_third_places"].iloc[0],
                    "todays_fourth_places": group["todays_fourth_places"].iloc[0],
                    "number_of_runs": group["number_of_runs"].iloc[0],
                    "todays_betfair_win_sp": group["todays_betfair_win_sp"].iloc[0],
                    "todays_betfair_place_sp": group["todays_betfair_place_sp"].iloc[0],
                    "todays_official_rating": group["todays_official_rating"].iloc[0],
                    "todays_days_since_last_ran": group[
                        "todays_days_since_last_ran"
                    ].iloc[0],
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

        return self.sanitize_nan(data)

    def format_todays_graph_data(
        self,
        data: pd.DataFrame,
        date_filter: str,
        filter_function: Callable,
        transformation_function: Callable,
        prices_filepath: str,
        date: str,
    ) -> list[dict]:
        data = self.create_todays_rating(data)
        data = self.format_todays_rating(data)
        data = (
            data.pipe(transformation_function, date, prices_filepath)
            .pipe(filter_function, date_filter)
            .pipe(
                self.convert_integer_columns,
                [
                    "official_rating",
                    "ts",
                    "rpr",
                    "tfr",
                    "tfig",
                    "rating",
                    "speed_figure",
                    "rolling_rating",
                    "rolling_speed_rating",
                ],
            )
        )
        performance_data = []
        for horse in data["horse_name"].unique():
            horse_data = data[data["horse_name"] == horse]
            performance_data.append(
                {
                    "horse_name": horse_data["horse_name"].iloc[0],
                    "horse_id": horse_data["horse_id"].iloc[0],
                    "initial_visibility": horse_data["initial_visibility"].iloc[0],
                    "performance_data": horse_data.to_dict(orient="records"),
                }
            )

        return performance_data

    def create_todays_rating(self, data: pd.DataFrame) -> pd.DataFrame:
        data["rank"] = data.groupby("horse_id")["race_date"].rank(
            ascending=False, method="dense"
        )
        data["race_time"] = pd.to_datetime(data["race_time"])
        today = pd.to_datetime(data[data["data_type"] == "today"]["race_date"].iloc[0])
        two_years_ago = today - pd.DateOffset(years=2)

        filtered_data = data[(data["race_time"] >= two_years_ago) & (data["rank"] <= 5)]

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

        result[["median_speed", "median_rating"]] = result[
            ["median_speed", "median_rating"]
        ].fillna(0)
        result[["mean_speed", "mean_rating"]] = result[
            ["mean_speed", "mean_rating"]
        ].fillna(0)

        return result

    def format_todays_rating(self, data: pd.DataFrame) -> pd.DataFrame:
        data["rating_tmp"] = (data["median_rating"] + data["mean_rating"]) / 2
        data["speed_rating_tmp"] = (data["median_speed"] + data["median_rating"]) / 2
        data["speed_figure"] = data["speed_figure"].fillna(data["speed_rating_tmp"])
        data["rating"] = data["rating"].fillna(data["rating_tmp"])
        data["rolling_rating"] = data["rating"].fillna(data["rating_tmp"])
        data["rolling_speed_rating"] = data["speed_figure"].fillna(
            data["speed_rating_tmp"]
        )
        data = data.drop(
            columns=[
                "rating_tmp",
                "speed_rating_tmp",
                "median_rating",
                "mean_rating",
                "median_speed",
                "mean_speed",
                "rank",
            ]
        )
        data["rating"] = data["rating"].round(0).astype(int)
        data["speed_figure"] = data["speed_figure"].round(0).astype(int)
        data["rolling_rating"] = data["rolling_rating"].round(0).astype(int)
        data["rolling_speed_rating"] = data["rolling_speed_rating"].round(0).astype(int)

        return data

    def sanitize_nan(self, data):
        """Replace NaN values with None in nested structures."""
        if isinstance(data, dict):
            return {k: self.sanitize_nan(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_nan(item) for item in data]
        elif isinstance(data, float) and np.isnan(data):
            return None
        return data
