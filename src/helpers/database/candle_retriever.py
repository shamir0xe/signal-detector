from libs.PythonLibrary.utils import debug_text
from typing import List
from src.models.candle import Candle
from src.facades.database import CryptoDB
from src.facades.config import Config

class CandleRetriever:
    @staticmethod
    def find(market: str, interval: str, start_time: int, end_time: int) -> List[Candle]:
        res = []
        start_time = str(int(start_time))
        end_time = str(int(end_time))
        # debug_text('(%, %) -- finding candles within this range: (%, %)', market, interval, start_time, end_time)
        # debug_text('seraching for %', {
        #     "provider": Config.get('provider'),
        #     "market": market,
        #     "interval": interval,
        #     "time": {
        #         "$gte": start_time,
        #         "$lte": end_time
        #     }
        # })
        cursor = CryptoDB.db().candles.find({
            "provider": Config.get('provider'),
            "market": market,
            "interval": interval,
            "time": {
                "$gte": start_time,
            }
        }).sort("time", +1)
        for obj in cursor:
            candle_data = [*obj['candle'], market.upper()]
            # debug_text('found a candle: %', Candle(*candle_data))
            res.append(Candle(*candle_data))
        return res
