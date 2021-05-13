from src.models.signal_statuses import SignalStatuses
from ...helpers.config.config_reader import ConfigReader
from libs.PythonLibrary.utils import debug_text
from typing import Dict, List
from ...models.price_types import PriceTypes
from src.models.signal_types import SignalTypes
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
        # debug_text('examining signal: %', signal)
        if signal.type is SignalTypes.LONG:
            return self.__examine_long(signal, data)
        return self.__examine_short(signal, data)

    def __examine_long(self, signal: Signal, data: List[Candle]) -> Dict:
        profit_point = signal.take_profit
        stop_limit = signal.stop_loss
        gain = 0
        status = SignalStatuses.PENDING
        index = signal.index + 1
        while index < len(data):
            if data[index].lowest < stop_limit:
                status = SignalStatuses.FAILED
                gain = self.__do_math(stop_limit, signal.candle.closing)
                break
            if data[index].highest > profit_point:
                status = SignalStatuses.DONE
                gain = self.__do_math(profit_point, signal.candle.closing)
                break
            if index - signal.index > self.config.get('signal_life'):
                status = SignalStatuses.DUMPED
                gain = self.__do_math(data[index].closing, signal.candle.closing)
                break
            index += 1
        # debug_text('LONG examining signal (%): status: %, gain: %', signal.candle.time, status, gain)
        return {
            "status": status,
            "gain": gain
        }

    def __examine_short(self, signal: Signal, data: List[Candle]) -> Dict:
        profit_point = signal.take_profit
        stop_limit = signal.stop_loss
        gain = 0
        status = SignalStatuses.PENDING
        index = signal.index + 1
        while (index < len(data)):
            if data[index].highest > stop_limit:
                status = SignalStatuses.FAILED
                gain = self.__do_math(signal.candle.openning, stop_limit)
                break
            if data[index].lowest < profit_point:
                status = SignalStatuses.DONE
                gain = self.__do_math(signal.candle.openning, profit_point)
                break
            if index - signal.index > self.config.get('signal_life'):
                status = SignalStatuses.DUMPED
                gain = self.__do_math(signal.candle.openning, data[index].closing)
                break
            index += 1
        # debug_text('SHORT examining signal (%): status: %, gain: %', signal.candle.time, status, gain)
        return {
            "status": status,
            "gain": gain
        }
    
    def __do_math(self, final_price: float, entry_price: float):
        return (final_price - entry_price) / entry_price
