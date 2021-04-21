from libs.PythonLibrary.utils import debug_text
import math
from typing import List

from ..models.signal_types import SignalTypes
from ..models.signal import Signal
from ..models.candle import Candle
from ..helpers.time_converter import TimeConverter


class SignalExaminator:
    def __init__(self) -> None:
        self.config = self.__read_config()

    def __read_config(self):
        return {
            'profit_factor': 0.03,
            'loss_factor': 0.03,
            'candle_margin': 3,
            'farthest_candle': 5,
            'signal_life': 15,
        }

    def do(self, signal: Signal, data: List[Candle]) -> int:
        if signal.type is SignalTypes.LONG:
            return self.examine_long(signal, data)
        return self.examin_short(signal, data)

    def examine_long(self, signal: Signal, data: List[Candle]) -> int:
        candle_size = self.__average_candle_size(signal, data)
        profit_point = signal.candle.closing + candle_size * self.config.get('candle_margin')
        stop_limit = signal.candle.closing - candle_size * self.config.get('candle_margin')
        debug_text('i:%, examining long: % -> (%, %)', signal.index, signal.candle.closing, stop_limit, profit_point)
        index = signal.index + 1
        while index < len(data):
            if index - signal.index > self.config.get('signal_life'):
                return -2
            if data[index].closing < stop_limit:
                debug_text('watafak, index: %, time: %', index, TimeConverter.seconds_to_timestamp(data[index].time))
                return -1
            if data[index].closing > profit_point:
                return +1
            index += 1
        return 0

    def __average_candle_size(self, signal: Signal, data: List[Candle]) -> float:
        index = signal.index
        start = max(0, index - self.config.get('farthest_candle'))
        end = min(len(data), index + self.config.get('farthest_candle'))
        s = sum([math.fabs(data[i].closing - data[i].openning) for i in range(start, end)])
        return s / (end - start)

    def examin_short(self, signal: Signal, data: List[Candle]) -> int:
        candle_size = self.__average_candle_size(signal, data)
        profit_point = signal.candle.closing - candle_size * self.config.get('candle_margin') 
        stop_limit = signal.candle.closing + candle_size * self.config.get('candle_margin')
        debug_text('i:%, examining short: % -> (%, %)', signal.index, signal.candle.closing, profit_point, stop_limit)
        index = signal.index + 1
        while (index < len(data)):
            if index - signal.index > self.config.get('signal_life'):
                return -2
            if data[index].closing > stop_limit:
                debug_text('watafak, index: %, time: %', index, TimeConverter.seconds_to_timestamp(data[index].time))
                return -1
            if data[index].closing < profit_point:
                return +1
            index += 1
        return 0
