from typing import Tuple
from src.adapters.interval_adapter import IntervalAdapter
import time

class CandleToTimestamp:
    @staticmethod
    def do(interval: str, candle_range: Tuple) -> int:
        seconds_interval = IntervalAdapter.plug(interval)
        cur_time = int(time.time())
        cur_time -= cur_time % seconds_interval
        return (
            cur_time + candle_range[0] * seconds_interval, 
            cur_time + candle_range[1] * seconds_interval
        )
