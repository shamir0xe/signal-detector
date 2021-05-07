from typing import Any, Dict, List
from src.models.trend_types import TrendTypes
from src.helpers.time.time_converter import TimeConverter

from src.helpers.indicators.ichimoku_calculator import IchimokuCalculator

from ..helpers.config.config_reader import ConfigReader

from .indicator_abstract import Indicator
from ..models.signal import Signal
from ..models.candle import Candle
from ..models.signal_types import SignalTypes
from libs.PythonLibrary.utils import debug_text
from src.helpers.chart.volume_oscilator_confirmator import VolumeOscilatorConfirmator
import math


class Ichimoku(Indicator):
    def __init__(self, data: List[Candle]) -> None:
        self.name = 'ichimoku'
        self.data = data[:-1]
        self.config = self.__read_config()
        self.signals = []
        self.lines = []
        self.small_window = self.config.get('window1')
        self.medium_window = self.config.get('window2')
        self.big_window = self.config.get('window3')

    def __read_config(self) -> Dict:
        return ConfigReader('indicators.ichimoku')
    
    def get_signals(self) -> List[Signal]:
        self.lines = IchimokuCalculator(self.data, self.config).calculate()
        signals = self.__calculate_signals()
        signals = self.__add_limits()
        return signals
        
    
    def __calculate_signals(self) -> List[Signal]:
        self.signals = []
        self.signals = [*self.signals, *self.__short_signals()]
        self.signals = [*self.signals, *self.__long_signals()]
        return self.signals

    def __add_limits(self) -> List[Signal]:
        for signal in self.signals:
            if signal.type is SignalTypes.LONG:
                delta = min(
                    self.data[signal.index].closing - self.lines[signal.index - self.medium_window]['cloud-bottom'],
                    math.fabs(self.data[signal.index].closing - self.lines[signal.index]['base'])
                )
                signal.stop_loss = self.data[signal.index].closing - delta 
                signal.take_profit = self.data[signal.index].closing + self.config.get('win-multiplier') * delta
        return self.signals

    def __short_signals(self) -> List[Signal]:
        res = []
        # over_boughts = OverBoughtCalculator().calculate(rsi, threshold=threshold, config=self.config)
        # for region in over_boughts:
        #     for index in region[-1:]:
        #         res.append(Signal(
        #             name = self.name, 
        #             type = SignalTypes.SHORT,
        #             candle = self.data[index],
        #             index = index
        #         ))
        return res

    def __long_condition_check(self, index) -> bool:
        bl = True
        bl &= self.data[index].closing > self.lines[index - self.medium_window]['cloud-top']
        bl &= self.lines[index]['conversion'] > self.lines[index]['base']
        bl &= self.lines[index]['cloud-green'] > self.lines[index]['cloud-red']
        bl &= self.data[index].closing > self.lines[index - 2 * self.medium_window]['cloud-top']
        return bl
        if bl:
            bl &= VolumeOscilatorConfirmator(self.data[:index + 1], {
                "min-volume-threshold": self.config.get("volume.min-volume-threshold"),
                "window-slow": self.config.get('volume.window-slow'),
                "window-fast": self.config.get('volume.window-fast')
            }).do(TrendTypes.UP)
        # if bl:
        #     debug_text('MANN time: %', TimeConverter.seconds_to_timestamp(self.data[index].time))
            # debug_text('data.closing = %', self.data[index].closing)
            # debug_text('cloud-green = %', self.lines[index - self.medium_window]['cloud-green'])
            # debug_text('cloud-red = %', self.lines[index - self.medium_window]['cloud-red'])
            # debug_text('conversion/base: % / %', self.lines[index]['conversion'], self.lines[index]['base'])
            # debug_text('self.lines: %', self.lines)
            # debug_text('top-line = %', self.lines[index - self.medium_window]['cloud-top'])
        return bl
    
    def __confirm_by_volume(self, index):
        return VolumeOscilatorConfirmator(self.data[:index + 1], {
            "min-volume-threshold": self.config.get("volume.min-volume-threshold"),
            "window-slow": self.config.get('volume.window-slow'),
            "window-fast": self.config.get('volume.window-fast')
        }).do(TrendTypes.UP)

    def __long_signals(self) -> List[Signal]:
        res = []
        oks = {}
        can_take = True
        for i in range(self.big_window, len(self.data)):
            if self.__long_condition_check(i):
                oks[i] = 1
            else:
                can_take = True
            if i in oks and self.__confirm_by_volume(i) and can_take:
                res.append(Signal(
                    self.name, 
                    SignalTypes.LONG, 
                    self.data[i], 
                    i
                ))
                can_take = False
        return res
