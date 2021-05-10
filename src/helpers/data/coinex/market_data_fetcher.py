import time
from typing import Any, List
from src.helpers.data.coinex.url_fetcher import UrlFetcher

class MarketDataFetcher:
    @staticmethod
    def fetch(market: str, interval: str, past_candles: int) -> List[List[Any]]:
        response = UrlFetcher('candle_data', market, interval, past_candles).fetch()
        try:
            response.raise_for_status()
        except:
            time.sleep(0.2)
            return MarketDataFetcher.fetch(market, interval, past_candles)
        return response.json()['data']

