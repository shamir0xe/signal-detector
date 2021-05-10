import requests
from src.adapters.coinex_adapter import CoinexAdapter

class UrlFetcher:
    def __init__(self, name, *args) -> None:
        self.name = name
        self.args = args
    
    def fetch(self) -> requests.Response:
        return getattr(self, 'fetch_' + self.name)(*self.args)
    
    def fetch_candle_data(self, market: str, interval: str, past_candles: int) -> requests.Response:
        adapter = CoinexAdapter(market=market, interval=interval, past_candles=past_candles)
        return requests.get("https://api.coinex.com/v1/market/kline", params=adapter.convert())

    def fetch_markets_data(self) -> requests.Response:
        return requests.get("https://api.coinex.com/v1/market/list")

