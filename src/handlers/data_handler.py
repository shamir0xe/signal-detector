import requests
from typing import Any, List
from libs.PythonLibrary.utils import debug_text
from ..adapters.coinex_adapter import CoinexAdapter
from ..models.candle import Candle

class DataFetcher:
    def __init__(self) -> None:
        self.url = ""

    def fetch(self, market: str, interval: int, past_days: int) -> List[Candle]:
        response = UrlFetcher('candle_data', market, interval, past_days).fetch()
        response.raise_for_status()
        data = response.json()['data']
        res = []
        for candle_info in data:
            res.append(Candle(*candle_info))
        return res

class UrlFetcher:
    def __init__(self, name, *args) -> None:
        self.name = name
        self.args = args
    
    def fetch(self) -> requests.Response:
        return getattr(self, 'fetch_' + self.name)(*self.args)
    
    def fetch_candle_data(self, market: str, interval: str, past_days: int) -> requests.Response:
        adapter = CoinexAdapter(market=market, interval=interval, past_days=past_days)
        return requests.get("https://api.coinex.com/v1/market/kline", params=adapter.convert())

