from libs.PythonLibrary.utils import debug_text
from typing import List
from src.models.candle import Candle
from src.facades.database import CryptoDB

class CandleRetriever:
    @staticmethod
    def find(market: str, interval: str, start_time: int, end_time: int) -> List[Candle]:
        res = []
        # debug_text('(%, %) -- finding candles within this range: (%, %)', market, interval, start_time, end_time)
        cursor = CryptoDB.db().candles.find({
            "market": market,
            "interval": interval,
            "time": {
                "$gte": int(start_time),
                "$lte": int(end_time)
            }
        }).sort("time", +1)
        for obj in cursor:
            res.append(Candle(*obj["candle"]))
            # debug_text('found a candle: %', Candle(*obj["candle"]))
        return res
