from typing import Any, Dict, List
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
from src.facades.config import Config


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
        signals = []
        for signal in self.signals:
            if signal.type is SignalTypes.LONG:
                # sl = IntervalDivider.do(
                #     start=self.lines[signal.index]['base'],
                #     end=self.lines[signal.index - self.medium_window]['cloud-bottom'],
                #     portion=0.66
                # )
                # signal.stop_loss = sl
                # signal.take_profit = 3 * self.data[signal.index].closing - 2 * sl
                delta = ATRCalculator(self.data[:signal.index + 1], {
                    'window': self.config.get('stoploss.window'),
                }).do()[-1] * self.config.get('stoploss.multiplier')
                signal.stop_loss = self.data[signal.index].lowest - delta
                signal.take_profit = self.data[signal.index].closing + delta * self.config.get('take-profit.multiplier')
                if signal.stop_loss > self.lines[signal.index - self.medium_window]['cloud-bottom']:
                    signals.append(signal)
        return signals

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


    def __rule_timer(self, index: int, rule_number: int) -> int:
        i = index
        while i >= 0 and self.__valid_rule(i, rule_number):
            i -= 1
        return i + 1

    def __valid_rule(self, index: int, rule_number: int) -> int:
        if rule_number == 1:
            # conversion line should be above the base line
            return self.lines[index]['conversion'] > self.lines[index]['base'] + 1e-6
        elif rule_number == 2:
            # lag-span should be above the candles
            return self.data[index].closing > self.data[index - self.medium_window].highest
        elif rule_number == 3:
            # candles should be above the cloud
            return self.data[index].closing > self.lines[index - self.medium_window]['cloud-top'] + 1e-6
        elif rule_number == 4:
            # right section of the cloud should be green
            return self.lines[index]['cloud-green'] > self.lines[index]['cloud-red'] + 1e-6
        elif rule_number == 5:
            # lag-span should be above the cloud
            return self.data[index].closing > self.lines[index - 2 * self.medium_window]['cloud-top'] + 1e-6
        elif rule_number == 6:
            # conversion line should be above the cloud
            return self.lines[index]['conversion'] > self.lines[index - self.medium_window]['cloud-top'] + 1e-6
        return False

    def __long_condition_check(self, index) -> bool:
        bl = True
        for i in range(6):
            bl &= self.__valid_rule(index, i + 1)
        if bl:
            t1 = self.__rule_timer(index, 1)
            t2 = self.__rule_timer(index, 2)
            t3 = self.__rule_timer(index, 3)
            # debug_text('MANN time: %', TimeConverter.seconds_to_timestamp(self.data[index].time))
            # debug_text('t1, t2, t3: %, %, %', t1, t2, t3)
            return t1 <= t3 and t2 <= t3
        # bl &= 2 * self.lines[index]['base'] - self.lines[index]['conversion'] > self.lines[index - self.medium_window]['cloud-top']
        # bl &= self.data[index].closing > self.lines[index]['ema']
        # bl &= self.lines[index]['cloud-green'] - self.lines[index]['cloud-red'] > \
        #     self.lines[index]['conversion'] - self.lines[index]['base']
        # if bl:
        #     debug_text('MANN time: %', TimeConverter.seconds_to_timestamp(self.data[index].time))
        #     debug_text('data.closing = %', self.data[index].closing)
        #     debug_text('ema(200): %', self.lines[index]['ema'])
        #     debug_text('cloud-green = %', self.lines[index - self.medium_window]['cloud-green'])
        #     debug_text('cloud-red = %', self.lines[index - self.medium_window]['cloud-red'])
        #     debug_text('conversion/base: % / %', self.lines[index]['conversion'], self.lines[index]['base'])
            # debug_text('self.lines: %', self.lines)
            # debug_text('top-line = %', self.lines[index - self.medium_window]['cloud-top'])
        return bl
    
    def __confirm_by_volume(self, index):
        # return True
        return VolumeOscilatorConfirmator(self.data[:index + 1], {
            "min-volume-threshold": self.config.get("volume.min-volume-threshold"),
            "window-slow": self.config.get('volume.window-slow'),
            "window-fast": self.config.get('volume.window-fast')
        }).do(TrendTypes.UP)

    def __confirm_by_trend(self, index):
        return True
        start = max(0, index - self.config.get('trend.window'))
        return self.data[index].lowest > self.data[start].highest
        return TrendConfirmator([candle.highest for candle in self.data[:index + 1]], {
            'window': self.config.get('trend.window')
        }) \
        .calculate_bounds(TrendTypes.UP) \
        .check()
    
    def __confirm_conversion_base_divergence(self, index):
        slope_conversion = TrendConfirmator([obj['conversion'] for obj in self.lines[:index + 1]], {
            'window': self.config.get('trend.divergence-window')
        }) \
        .calculate_bounds(TrendTypes.UP) \
        .trend_slope()

        slope_base = TrendConfirmator([obj['base'] for obj in self.lines[:index + 1]], {
            'window': self.config.get('trend.divergence-window')
        }) \
        .calculate_bounds(TrendTypes.UP) \
        .trend_slope()

        # if "05/03" in TimeConverter.seconds_to_timestamp(self.data[index].time):
        #     debug_text('~~time: %', TimeConverter.seconds_to_timestamp(self.data[index].time))
        #     debug_text('slopes: conv=%, base=%', slope_conversion, slope_base)
 
        return slope_conversion > slope_base + 1e-5

    def __long_signals(self) -> List[Signal]:
        res = []
        oks = {}
        for i in range(self.big_window, len(self.data)):
            bl = False
            if self.__long_condition_check(i) and \
                self.__confirm_by_volume(i) and \
                self.__confirm_by_trend(i) and \
                self.__confirm_conversion_base_divergence(i):
                bl = True
            for j in range(Config.get('models.signal.life') >> 1):
                bl &= not ((i - j - 1) in oks)
            if bl:
                res.append(Signal(
                    self.name, 
                    SignalTypes.LONG, 
                    self.data[i], 
                    i
                ))
                oks[i] = 1
        return res
