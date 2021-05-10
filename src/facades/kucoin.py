from __future__ import annotations
import time
from typing import Any
from kucoin.client import Market, Trade

class Kucoin:
    URL = 'https://api.kucoin.com'
    def __init__(self, config) -> None:
        self.config = config

    def market_client(self) -> MarketClient:
        return MarketClient(url=Kucoin.URL)

    def init_trade_client(self) -> Trade:
        self.trade_client = Trade(
            key=self.config.get('key'),
            secret=self.config.get('secret'),
            passphrase=self.config.get('passphrase'),
            is_sandbox=False,
            url=Kucoin.URL
        )
        return self.trade_client

class MarketClient(Market):
    MAX_QUERIES = {
        'count': 30,
        'time': 10
    }
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.queries = []

    def rate_limit(self) -> MarketClient:
        self.queries.append(time.time())
        if len(self.queries) < MarketClient.MAX_QUERIES['count']:
            return self
        seconds = MarketClient.MAX_QUERIES['time'] - (self.queries[-1] - self.queries[0])
        if seconds > 0:
            time.sleep(seconds)
        self.queries = self.queries[1:]
        return self

