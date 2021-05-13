from typing import Any
from src.facades.kucoin import MarketClient

class MarketListFetcher:
    @staticmethod
    def do(market_client: MarketClient) -> Any:
        return market_client \
            .rate_limit() \
            .get_currencies()
