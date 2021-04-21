import math
from typing import Any
from ..helpers.time.time_converter import TimeConverter

class Candle:
    def __init__(
        self, 
        time: int, 
        openning: float, 
        closing: float, 
        highest: float,
        lowest: float,
        volume: float,
        amount: float,
        market: str
    ) -> None:
        self.time = int(time)
        self.openning = float(openning)
        self.closing = float(closing)
        self.highest = float(highest)
        self.lowest = float(lowest)
        self.volume = float(volume)
        self.amount = float(amount)
        self.market = market


    def get(self, attribute: str) -> Any:
        return getattr(self, attribute)
    
    def get_size(self) -> float:
        return math.fabs(self.closing - self.openning)

    def __str__(self) -> str:
        return '[market: {}, time: {}, o: {}, c: {}, h: {}, l: {}, v: {}, amount: {}]'.format(
            self.market,
            TimeConverter.seconds_to_timestamp(self.time),
            self.openning,
            self.closing,
            self.highest,
            self.lowest,
            self.volume,
            self.amount
        )
