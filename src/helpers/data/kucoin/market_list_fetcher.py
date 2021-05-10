import json
from mmap import PAGESIZE
from typing import Any, Dict

from kucoin.client import Market
from src.helpers.config.environment_reader import EnvironmentReader
from src.facades.kucoin import MarketClient

class MarketListFetcher:
    @staticmethod
    def do(market_client: MarketClient) -> Any:
        return market_client \
            .rate_limit() \
            .get_currencies()
