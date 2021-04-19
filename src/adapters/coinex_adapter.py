from typing import Optional


class CoinexAdapter:
    def __init__(
        self, 
        market: Optional[str], 
        interval: Optional[int], 
        past_days: Optional[int]
    ) -> None:
        self.name = 'coinex'
        self.market = market
        self.interval = interval
        self.past_days = past_days

    def convert(self):
        res = {}
        if self.market is not None:
            res['market'] = self.market.upper()
        if self.interval is not None:
            res['type'] = self.interval
        if self.past_days is not None:
            res['limit'] = self.past_days
        return res
