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
    
import math
import numpy as np

    def sanitize(data):
        if isinstance(data, float):
            if math.isinf(data) or math.isnan(data):
                return None  # or a specific value you deem appropriate
        elif isinstance(data, dict):
            return {k: sanitize(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [sanitize(item) for item in data]
        return data
