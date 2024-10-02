import pandas as pd
from fastapi import Depends

from api_helpers.s3_client import S3Client
from src.helpers.s3_client import get_s3_client


class PricesRepository:
    def __init__(self, s3_client: S3Client):
        self.s3_client = s3_client

    async def get_current_prices(self) -> pd.DataFrame:
        return self.s3_client.fetch_latest_price_changes("price_changes/")


def get_prices_repository(s3_client: S3Client = Depends(get_s3_client)):
    return PricesRepository(s3_client)
