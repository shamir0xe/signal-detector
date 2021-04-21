import math
from libs.PythonLibrary.geometry import Geometry
from typing import Any, Dict, List

from .indicator_abstract import Indicator
from ..models.signal import Signal
from ..models.candle import Candle
from ..models.signal_types import SignalTypes
from libs.PythonLibrary.utils import debug_text
from ..helpers.rsi_calculator import RsiCalculator
from ..helpers.overbought_calculator import OverBoughtCalculator
from ..helpers.oversold_calculator import OverSoldCalculator
from ..helpers.show_plot import ShowGeometryPlot
from ..helpers.convex_calculator import LowerBoundConvex, UpperBoundConvex
from ..helpers.time_converter import TimeConverter


class RsiDivergence(Indicator):
    def __init__(self, data: List[Candle]) -> None:
        self.name = 'rsi-divergence'
        self.data = data
        self.config = self.__read_config()

    def __read_config(self) -> Dict:
        return {
            'max_pick_distance': 10,
            'upperbound_threshold': 60,
            'lowerbound_threshold': 40,
        }
    
    def get_signals(self) -> List[Signal]:
        res = []
        rsi = RsiCalculator(self.data, self.config).calculate()

        up_threshold = self.config.get('upperbound_threshold')
        res = [*res, *self.__short_signals(rsi, up_threshold)]

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

    def __short_signals(self, rsi: Any, threshold: float) -> List[Signal]:
        res = []
        over_boughts = OverBoughtCalculator().calculate(rsi, threshold=threshold, config=self.config)
        over_boughts = self.__union(over_boughts)
        picks = self.__high_picks(over_boughts, rsi)
        for i in picks:
            for j in picks:
                if i > j - 2 or abs(i - j) > self.config.get('max_pick_distance'):
                    continue
                if rsi[i] >= rsi[j] + 1.5 and max(rsi[i:j + 1]) == rsi[i]:
                    # ShowGeometryPlot.do([Geometry.Point(i, rsi[i]), Geometry.Point(j, rsi[j])])
                    upper_bounds = UpperBoundConvex([Geometry.Point(k, self.data[k].closing) for k in range(i, j + 1)]).do()
                    index_array = [round(point.x) for point in upper_bounds]
                    index_array = index_array[::-1]
                    border_lines = [
                        [(index_array[i], index_array[i + 1]), 
                        math.fabs(sum([self.data[j].volume for j in range(index_array[i], index_array[i + 1])]))]
                        for i in range(len(index_array) - 1)
                    ]
                    border_lines.sort(key=lambda weighted_line: -weighted_line[1])
                    # for border in border_lines:
                    #     debug_text('border-line: %', border)
                    major_indices = border_lines[0][0] 
                    c1 = self.data[major_indices[0]]
                    c2 = self.data[major_indices[1]]
                    if c1.closing + self.__average_candle_length(c1, c2) / 4 < c2.closing:
                        # debug_text('YEAY we have signal')
                        debug_text('% -> %', TimeConverter.seconds_to_timestamp(self.data[i].time), TimeConverter.seconds_to_timestamp(self.data[j].time))
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
                if i > j - 2 or abs(i - j) > self.config.get('max_pick_distance'):
                    continue
                if rsi[i] + 1.5 <= rsi[j] and min(rsi[i:j + 1]) == rsi[i]:
                    # ShowGeometryPlot.do([Geometry.Point(i, rsi[i]), Geometry.Point(j, rsi[j])])
                    lower_bounds = LowerBoundConvex([Geometry.Point(k, self.data[k].closing) for k in range(i, j + 1)]).do()
                    index_array = [round(point.x) for point in lower_bounds]
                    index_array = index_array[::-1]
                    border_lines = [
                        [(index_array[i], index_array[i + 1]), 
                        math.fabs(sum([self.data[j].volume for j in range(index_array[i], index_array[i + 1])]))]
                        for i in range(len(index_array) - 1)
                    ]
                    border_lines.sort(key=lambda weighted_line: -weighted_line[1])
                    # for border in border_lines:
                        # debug_text('border-line: %', border)
                    major_indices = border_lines[0][0] 
                    c1 = self.data[major_indices[0]]
                    c2 = self.data[major_indices[1]]
                    if c2.closing + self.__average_candle_length(c1, c2) / 4 < c1.closing:
                        # debug_text('HELL YEA!')
                        res.append(Signal(
                            name = self.name,
                            type = SignalTypes.LONG,
                            strength = 0,
                            candle = self.data[j],
                            index = j,
                        ))
        return res

