from typing import Any, Dict, List
from src.helpers.trend.trend_calculator import TrendCalculator
from libs.PythonLibrary.utils import debug_text
from .indicator_abstract import Indicator
from src.models.trend_types import TrendTypes
from src.helpers.time.time_converter import TimeConverter
from src.helpers.indicators.ichimoku_calculator import IchimokuCalculator
from src.helpers.config.config_reader import ConfigReader
from src.models.signal import Signal
from src.models.candle import Candle
from src.models.signal_types import SignalTypes
from src.helpers.chart.volume_oscilator_confirmator import VolumeOscilatorConfirmator
from src.helpers.chart.trend_confirmator import TrendConfirmator
from src.helpers.chart.interval_divider import IntervalDivider
from src.helpers.chart.atr_calculator import ATRCalculator
from src.helpers.chart.key_level_calculator import KeyLevelCalculator
from src.helpers.chart.candlestick_calculator import CandlestickCalculator
from src.facades.config import Config


class CandlestickPattern(Indicator):
    def __init__(self, data: List[Candle]) -> None:
        self.name = 'candlestick-pattern'
        self.data = data[::]
        self.config = self.__read_config()
        self.signals = []

    def __read_config(self) -> Dict:
        return ConfigReader('indicators.candlestick-pattern')
    
    def get_signals(self) -> List[Signal]:
        signals = self.__calculate_signals()
        signals = self.__add_limits()
        return signals


    def __calculate_signals(self) -> List[Signal]:
        self.signals = []
        self.signals = [*self.signals, *self.__short_signals()]
        self.signals = [*self.signals, *self.__long_signals()]
        return self.signals

    def __add_limits(self) -> List[Signal]:
        signals = []
        for signal in self.signals:
            if signal.type is SignalTypes.LONG:
                # delta = ATRCalculator(self.data[:signal.index + 1], {
                #     'window': self.config.get('stoploss.window'),
                # }).do()[-1] * self.config.get('stoploss.multiplier')
                # signal.stop_loss = self.data[signal.index].lowest - delta
                # signal.take_profit = self.data[signal.index].closing + delta * self.config.get('take-profit.multiplier')
                signals.append(signal)
        return signals

    def __short_signals(self) -> List[Signal]:
        res = []
        return res

    def __long_signals(self) -> List[Signal]:
        res = []
        calculator = KeyLevelCalculator(self.data[:self.config.get('key-level.left-window')], {
            'left-window': self.config.get('key-level.left-window'),
            'right-window': self.config.get('key-level.right-window')
        })
        for i in range(self.config.get('key-level.left-window'), len(self.data)):
            key_levels = calculator.add_candle(self.data[i])
            key_levels = [key_level for key_level in key_levels if key_level.count >= self.config.get('key-level.min-count') and i - key_level.index <= self.config.get('key-level.window')]
            points, level = CandlestickCalculator(
                data=self.data[i - self.config.get('key-level.left-window'):i + 1],
                key_levels=key_levels
            ).do(TrendTypes.UP)
            if points >= self.config.get('minimum-points'):
                # debug_text('key level selected: %', level)
                sl = min(level.level, self.data[i].lowest)
                tp = self.data[i].closing + (self.data[i].closing - sl) * self.config.get('take-profit.multiplier')
                # debug_text('sl, tp: %, %', sl, tp)
                # debug_text('\nkey levels are as follow:')
                # for key_level in key_levels:
                #     debug_text('key level: %', key_level)
                res.append(Signal(
                    name=self.name,
                    signal_type=SignalTypes.LONG,
                    candle=self.data[i],
                    index=i,
                    take_profit=tp,
                    stop_loss=sl
                ))
        return res
