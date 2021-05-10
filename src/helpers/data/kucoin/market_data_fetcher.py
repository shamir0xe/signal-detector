from src.helpers.time.time_converter import TimeConverter
from libs.PythonLibrary.utils import debug_text
import time
from typing import Any, List
from src.facades.kucoin import MarketClient
from src.adapters.kucoin_adapter import KucoinAdapter
from src.helpers.time.candle_to_timestamp import CandleToTimestamp

class MarketDataFetcher:
    @staticmethod
    def fetch(
        market_client: MarketClient, 
        market: str, 
        interval: int, 
        past_candles: int
    ) -> List[List[Any]]:
        market = KucoinAdapter.market_plug(market)
        start_at, end_at = CandleToTimestamp.do(
            interval=interval, 
            candle_range=(-past_candles + 1, 1)
        )
        # debug_text('interval to get kline: (%, %)', start_at, end_at)
        # debug_text('(%, %)', TimeConverter.seconds_to_timestamp(start_at), 
        # TimeConverter.seconds_to_timestamp(end_at))
        return market_client \
            .rate_limit() \
            .get_kline(
                symbol=market, 
                kline_type=interval, 
                startAt=start_at, 
                endAt=end_at
            )
