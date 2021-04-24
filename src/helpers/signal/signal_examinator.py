from ...helpers.config.config_reader import ConfigReader
from libs.PythonLibrary.utils import debug_text
from typing import List
from ...models.price_types import PriceTypes
from ...models.signal_types import SignalTypes
from ...models.signal import Signal
from ...models.candle import Candle
from ..price.price_calculator import PriceCalculator
from ...helpers.time.time_converter import TimeConverter

class SignalExaminator:
    def __init__(self) -> None:
        self.config = self.__read_config()

    def __read_config(self):
        return ConfigReader('helpers.signal.signal-examinator')

    def do(self, signal: Signal, data: List[Candle]) -> int:
        if signal.type is SignalTypes.LONG:
            return self.__examine_long(signal, data)
        return self.__examine_short(signal, data)

    def __examine_long(self, signal: Signal, data: List[Candle]) -> int:
        profit_point = PriceCalculator(data, signal).do(PriceTypes.SELL_PRICE)
        stop_limit = PriceCalculator(data, signal).do(PriceTypes.STOP_LOSS)
        # debug_text('i:%, examining long: % -> (%, %)', signal.index, signal.candle.closing, stop_limit, profit_point)
        index = signal.index + 1
        while index < len(data):
            if index - signal.index > self.config.get('signal_life'):
                return -2
            if data[index].closing < stop_limit:
                # debug_text('watafak, index: %, time: %', index, TimeConverter.seconds_to_timestamp(data[index].time))
                return -1
            if data[index].closing > profit_point:
                return +1
            index += 1
        return 0

    def __examine_short(self, signal: Signal, data: List[Candle]) -> int:
        profit_point = PriceCalculator(data, signal).do(PriceTypes.SELL_PRICE)
        stop_limit = PriceCalculator(data, signal).do(PriceTypes.STOP_LOSS)
        # debug_text('i:%, examining short: % -> (%, %)', signal.index, signal.candle.closing, profit_point, stop_limit)
        index = signal.index + 1
        while (index < len(data)):
            if index - signal.index > self.config.get('signal_life'):
                return -2
            if data[index].closing > stop_limit:
                # debug_text('watafak, index: %, time: %', index, TimeConverter.seconds_to_timestamp(data[index].time))
                return -1
            if data[index].closing < profit_point:
                return +1
            index += 1
        return 0
