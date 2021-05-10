import math

from typing import Any, Dict, List

from src.helpers.chart.atr_calculator import ATRCalculator
from ..models.trend_types import TrendTypes
from .indicator_abstract import Indicator
from ..models.signal import Signal
from ..models.candle import Candle
from ..models.signal_types import SignalTypes
from libs.PythonLibrary.utils import debug_text
from ..helpers.indicators.rsi_calculator import RsiCalculator
from ..helpers.chart.overbought_calculator import OverBoughtCalculator
from ..helpers.chart.oversold_calculator import OverSoldCalculator
from ..helpers.geometry.show_plot import ShowGeometryPlot
from ..helpers.time.time_converter import TimeConverter
from ..helpers.geometry.convex_path_check import ConvexPathCheck
from ..helpers.trend.trend_calculator import TrendCalculator
from ..helpers.config.config_reader import ConfigReader



class RsiDivergence(Indicator):
    def __init__(self, data: List[Candle]) -> None:
        self.name = 'rsi-divergence'
        self.data = data
        self.config = self.__read_config()

    def __read_config(self) -> ConfigReader:
        return ConfigReader('indicators.rsi-divergence');
    
    def get_signals(self) -> List[Signal]:
        res = []
        rsi = RsiCalculator(self.data, self.config).calculate()

        up_threshold = self.config.get('upperbound_threshold')
        # res = [*res, *self.__short_signals(rsi, up_threshold)]

        lo_threshold = self.config.get('lowerbound_threshold')
        res = [*res, *self.__long_signals(rsi, lo_threshold)]
        return res
   
    def __high_picks(self, over_boughts: List[int], rsi: Any) -> List[int]:
        picks = []
        for index in over_boughts:
            if index - 1 >= 0 and index + 1 < len(rsi):
                if rsi[index] > rsi[index + 1] and rsi[index] > rsi[index - 1]:
                    picks.append(index)
        return picks
    
    def __low_picks(self, over_solds: List[int], rsi: Any) -> List[int]:
        res = []
        for i in over_solds:
            if i - 1 >= 0 and i + 1 < len(rsi):
                if rsi[i] < rsi[i - 1] and rsi[i] < rsi[i + 1]:
                    res.append(i)
        return res

    def __union(self, regions: List[List[int]]) -> List[int]:
        res = []
        for region in regions:
            res = [*res, *region]
        return res
    
    def __average_candle_length(self, *candles: Candle) -> float:
        s = sum([math.fabs(candle.openning - candle.closing) for candle in candles])
        return s / len(candles)

    def __check_rsi_short(self, rsi: Any, i: int, j: int) -> bool:
        return rsi[i] >= rsi[j] + self.config.get('min_rsi_diff')
    
    def __check_rsi_long(self, rsi: Any, i: int, j: int) -> bool:
        return rsi[i] + self.config.get('min_rsi_diff') <= rsi[j]
    
    def __check_slope_short(self, i: int, j: int) -> bool:
        if self.data[i].closing >= self.data[j].closing:
            return False
        slope = (self.data[j].closing - self.data[i].closing) / ((sum([candle.get_size() for candle in self.data[i + 1:j + 1]]) / (j - i)) * (j - i))
        # debug_text('short slope: %/%', slope, self.config.get('min_slope'))
        return slope > self.config.get('min_slope')

    def __check_slope_long(self, i: int, j: int) -> bool:
        if self.data[i].closing <= self.data[j].closing:
            return False
        slope = (self.data[i].closing - self.data[j].closing) / ((sum([candle.get_size() for candle in self.data[i + 1:j + 1]]) / (j - i)) * (j - i))
        # debug_text('long slope: %/%', slope, self.config.get('min_slope'))
        return slope > self.config.get('min_slope')

    def __short_signals(self, rsi: Any, threshold: float) -> List[Signal]:
        res = []
        over_boughts = OverBoughtCalculator().calculate(rsi, threshold=threshold, config=self.config)
        over_boughts = self.__union(over_boughts)
        picks = self.__high_picks(over_boughts, rsi)
        for i in picks:
            for j in picks:
                if i > j - 1 or abs(i - j) > self.config.get('max_pick_distance'):
                    continue
                if self.__check_rsi_short(rsi, i, j):
                    if not ConvexPathCheck(rsi, range(i, j + 1)).do(TrendTypes.UP):
                        continue
                    trendline = TrendCalculator(
                        [candle.closing for candle in self.data], 
                        range(i, j + 1), 
                        [candle.volume for candle in self.data]
                    ).do(TrendTypes.UP)
                    # trendline = UpperTrendCalculator(self.data, range(i, j + 1)).do("closing")
                    c1 = self.data[round(trendline.p1.x)]
                    c2 = self.data[round(trendline.p2.x)]
                    if self.__check_slope_short(round(trendline.p1.x), round(trendline.p2.x)):
                    # if c1.closing + self.__average_candle_length(c1, c2) / 4 < c2.closing:
                        # debug_text('% -> %', TimeConverter.seconds_to_timestamp(self.data[i].time), TimeConverter.seconds_to_timestamp(self.data[j].time))
                        res.append(Signal(
                            name = self.name,
                            type = SignalTypes.SHORT,
                            strength = 0,
                            candle = self.data[j],
                            index = j
                        ))
        return res

    def __long_signals(self, rsi: Any, threshold: float) -> List[Signal]:
        res = []
        over_sold = OverSoldCalculator().calculate(rsi, threshold=threshold, config=self.config)
        over_sold = self.__union(over_sold)
        picks = self.__low_picks(over_sold, rsi)
        for i in picks:
            for j in picks:
                if i > j - 1 or abs(i - j) > self.config.get('max_pick_distance'):
                    continue
                if self.__check_rsi_long(rsi, i, j):
                    if not ConvexPathCheck(rsi, range(i, j + 1)).do(TrendTypes.DOWN):
                        continue
                    trendline = TrendCalculator(
                        [candle.closing for candle in self.data],
                        range(i, j + 1),
                        [candle.volume for candle in self.data]
                    ).do(TrendTypes.DOWN)
                    # trendline = LowerTrendCalculator(self.data, range(i, j + 1)).do("closing")
                    c1 = self.data[round(trendline.p1.x)]
                    c2 = self.data[round(trendline.p2.x)]
                    if self.__check_slope_long(round(trendline.p1.x), round(trendline.p2.x)):
                    # if c2.closing + self.__average_candle_length(c1, c2) / 4 < c1.closing:
                        # debug_text('% -> %', TimeConverter.seconds_to_timestamp(self.data[i].time), TimeConverter.seconds_to_timestamp(self.data[j].time))
                        delta = ATRCalculator(self.data[:j + 1], {
                            'window': self.config.get('stoploss.window'),
                        }).do()[-1] * self.config.get('stoploss.multiplier')
                        res.append(Signal(
                            name = self.name,
                            type = SignalTypes.LONG,
                            candle = self.data[j],
                            index = j,
                            take_profit=self.data[j].closing + self.config.get('take-profit.multiplier') * delta,
                            stop_loss=self.data[j].lowest - delta
                        ))
                        # except:
                        #     debug_text('i, j -> (%, %)', i, j)
                        #     for candle in self.data[:j + 1]:
                        #         debug_text('    ~~~candle: %', candle)
                        
        return res

