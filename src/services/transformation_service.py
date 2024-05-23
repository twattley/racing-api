from datetime import datetime
import numpy as np
import pandas as pd


class TransformationService:
    def __init__(self):
        pass

    def _create_tmp_vars(self, data: pd.DataFrame, date: str) -> pd.DataFrame:
        return data.assign(
            race_date_tmp=pd.to_datetime(data["race_date"], errors="coerce"),
            todays_date_tmp=pd.to_datetime(date, errors="coerce"),
        )

    def _create_days_since_performance(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.assign(
            days_since_performance=(
                data["todays_date_tmp"] - data["race_date_tmp"]
            ).dt.days
        )
        data .to_csv('~/Desktop/test.csv', index=False)
        return data

    def _cleanup_temp_vars(self, data: pd.DataFrame) -> pd.DataFrame:
        return data.drop(columns=["race_date_tmp", "todays_date_tmp"])

    def calculate(self, data: pd.DataFrame, date: str) -> pd.DataFrame:

        return (
            self._create_tmp_vars(data, date)
            .pipe(self._create_days_since_performance)
            .pipe(self._cleanup_temp_vars)
        )
