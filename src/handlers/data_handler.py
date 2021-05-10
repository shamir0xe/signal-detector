import requests
from typing import Any, List
from src.facades.kucoin import MarketClient
from src.helpers.config.environment_reader import EnvironmentReader
from libs.PythonLibrary.utils import debug_text
from ..adapters.coinex_adapter import CoinexAdapter
from ..models.candle import Candle
import time
from src.facades.config import Config
import src.helpers.data.coinex.market_data_fetcher as coinex
import src.helpers.data.kucoin.market_data_fetcher as kucoin
from src.facades.kucoin import Kucoin

class DataFetcher:
    def __init__(self) -> None:
        self.url = ""
        env = EnvironmentReader()
        self.market_client = Kucoin({
            'key': env.get('key'),
            'secret': env.get('secret'),
            'passphrase': env.get('passphrase')
        }).market_client()

    def fetch(self, market: str, interval: int, past_days: int) -> List[Candle]:
        provider = Config.get('provider')
        if provider == 'coinex':
            data = coinex.MarketDataFetcher.fetch(
                market=market,
                interval=interval,
                past_candles=past_days
            )
        if provider == "kucoin":
            data = kucoin.MarketDataFetcher.fetch(
                market_client=self.market_client,
                market=market,
                interval=interval,
                past_candles=past_days,
            )
        data.sort(key=lambda candle_data: int(candle_data[0]))
        res = []
        for candle_data in data:
            # debug_text('candle: %', Candle(*candle_data))
            res.append(Candle(*candle_data))
        return res
