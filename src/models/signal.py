from __future__ import annotations
from typing import Tuple
from src.models.signal_statuses import SignalStatuses

from src.helpers.config.config_reader import ConfigReader
from src.helpers.time.time_converter import TimeConverter
from .candle import Candle
from .signal_types import SignalTypes


class Signal:
    def __init__(
        self, 
        name: str,
        signal_type: SignalTypes,
        candle: Candle,
        index: int,
        take_profit: float = -1,
        stop_loss: float = -1
    ) -> None:
        self.name = name
        self.type = signal_type
        self.candle = candle
        self.index = index
        self.status = SignalStatuses.PENDING
        self.original_candle = None
        self.take_profit = take_profit
        self.stop_loss = stop_loss
        self.gain = 0
        self.config = ConfigReader('models.signal')
        if self.take_profit < 0:
            self.take_profit, self.stop_loss = self.__calculate_limits()
    
    def __calculate_limits(self) -> Tuple[float, float]:
        if self.type is SignalTypes.LONG:
            return (
                self.candle.closing * (1 + self.config.get('win-percent')), 
                self.candle.closing * (1 - 0.5 * self.config.get('win-percent'))
            )
        return (
            self.candle.closing * (1 - self.config.get('win-percent')),
            self.candle.closing * (1 + 0.5 * self.config.get('win-percent'))
        )
    
    def set_status(self, status: SignalStatuses) -> None:
        self.status = status
    
    def set_gain(self, gain: float) -> None:
        self.gain = gain
    
    def equals(self, signal: Signal) -> bool:
        bl = True
        bl &= self.name == signal.name
        bl &= self.type == signal.type
        bl &= self.index == signal.index
        return bl

    def __str__(self) -> str:
        return '[{}/{} - t:{} - succeed:{}'.format(
            self.name, 
            self.type, 
            TimeConverter.seconds_to_timestamp(self.candle.time), 
            self.status
        )

