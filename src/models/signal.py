from ..helpers.time_converter import TimeConverter
from .candle import Candle
from .signal_types import SignalTypes


class Signal:
    def __init__(
        self, 
        name: str,
        type: SignalTypes,
        strength: float,
        candle: Candle,
        index: int
    ) -> None:
        self.name = name
        self.type = type
        self.strength = strength
        self.candle = candle
        self.index = index
        self.status = 0
        self.original_candle = None
    
    def set_status(self, status: int) -> None:
        self.status = status

    def __str__(self) -> str:
        return '[{}/{} - t:{} - s:{} - succeed:{}'.format(
            self.name, 
            self.type, 
            TimeConverter.seconds_to_timestamp(self.candle.time), 
            self.strength, 
            self.status
        )
