import pandas as pd

from api_helpers.betfair_client import (
    get_betfair_client,
    BetfairCredentials,
    BetfairClient,
)
from src.config import config

class BetfairService:
    trading_client: BetfairClient

    def __init__(self, trading_client: BetfairClient):
        self.trading_client = trading_client

    async def get_current_market_data(self):
        return await self.trading_client.create_market_data()


def get_betfair_service():
    trading_client = get_betfair_client(
        BetfairCredentials(
            username=config.bf_username,
            password=config.bf_password,
            app_key=config.bf_app_key,
            certs_path=config.bf_certs_path,
        )
    )
    return BetfairService(trading_client)
