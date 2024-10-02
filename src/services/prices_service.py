
from fastapi import Depends



from ..repository.prices_repository import PricesRepository, get_prices_repository
from .base_service import BaseService


class PricesService(BaseService):
    def __init__(
        self,
        prices_repository: PricesRepository,
    ):
        self.prices_repository = prices_repository

    def get_current_prices(self):
        return self.prices_repository.get_current_prices()


def get_prices_service(
    prices_repository: PricesRepository = Depends(get_prices_repository),
):
    return PricesService(prices_repository)
