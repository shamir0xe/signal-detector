from src.models.signal_statuses import SignalStatuses
from src.helpers.config.config_reader import ConfigReader
from libs.PythonLibrary.utils import debug_text
from typing import Dict, List
from src.models.price_types import PriceTypes
from src.models.signal_types import SignalTypes
from src.models.signal import Signal
from src.models.candle import Candle
from src.helpers.price.price_calculator import PriceCalculator
from src.helpers.time.time_converter import TimeConverter
from src.facades.config import Config

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
        # profit_point = signal.take_profit 
        # stop_limit = signal.stop_loss 
        profit_point = signal.take_profit - signal.candle.closing
        stop_limit = signal.stop_loss - signal.candle.closing
        gain = 0
        status = SignalStatuses.PENDING
        real_init_index = signal.index + 1
        index = real_init_index + 1
        if real_init_index < len(data):
            profit_point += data[real_init_index].closing
            stop_limit += data[real_init_index].closing
            while index < len(data):
                # if "Mon 21/05/24" in TimeConverter.seconds_to_timestamp(signal.candle.time):
                #     debug_text('time, highest, tp: %, %, %', TimeConverter.seconds_to_timestamp(data[index].time), data[index].highest, signal.take_profit)
                if data[index].lowest < stop_limit:
                    status = SignalStatuses.FAILED
                    gain = self.__do_math(stop_limit, data[real_init_index].closing)
                    break
                if data[index].highest > profit_point:
                    status = SignalStatuses.DONE
                    gain = self.__do_math(profit_point, data[real_init_index].closing)
                    break
                if index - real_init_index > Config.get('models.signal.life'):
                    status = SignalStatuses.DUMPED
                    gain = self.__do_math(data[index].closing, data[real_init_index].closing)
                    break
                index += 1
        # debug_text('LONG examining signal (%): status: %, gain: %', signal.candle.time, status, gain)
        return {
            "status": status,
            "gain": gain,
            'life': index - real_init_index
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
                gain = -self.__do_math(stop_limit, signal.candle.closing)
                break
            if data[index].lowest < profit_point:
                status = SignalStatuses.DONE
                gain = -self.__do_math(profit_point, signal.candle.closing)
                break
            if index - signal.index > Config.get('models.signal.life'):
                status = SignalStatuses.DUMPED
                gain = -self.__do_math(data[index].closing, signal.candle.closing)
                break
            index += 1
        # debug_text('SHORT examining signal (%): status: %, gain: %', signal.candle.time, status, gain)
        return {
            "status": status,
            "gain": gain
        }
    
    def __do_math(self, final_price: float, entry_price: float):
        return (final_price - entry_price) / entry_price
