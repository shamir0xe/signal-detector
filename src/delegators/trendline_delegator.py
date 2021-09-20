from __future__ import annotations
import math

from numpy.core.defchararray import index
from libs.PythonLibrary.utils import debug_text
from libs.PythonLibrary.geometry import Geometry
from math import fabs
from typing import Dict, List
from src.models.trend_types import TrendTypes
from src.models.signal_types import SignalTypes
from src.models.signal import Signal
from src.models.candle import Candle
from src.helpers.geometry.show_plot import ShowGeometryPlot
from src.helpers.trend.trend_calculator import TrendCalculator
from src.helpers.config.config_reader import ConfigReader

class TrendlineDelegator:
    def __init__(self, signal: Signal, data: List[Candle]) -> None:
        self.signal = signal
        self.data = data
        self.index = self.signal.index
        self.config = self.__read_config()
        self.trendline = None
        self.pass_weight = True

    def __read_config(self) -> Dict:
        return ConfigReader('delegators.trend-line-delegator')

    def downtrend(self) -> TrendlineDelegator:
        self.trendline = TrendCalculator(
            [candle.openning for candle in self.data], 
            self.find_range(), 
            [candle.volume for candle in self.data]
        ).do(TrendTypes.UP)
        # self.trendline = UpperTrendCalculator(self.data, self.find_range()).do("openning")
        return self

    def uptrend(self) -> TrendlineDelegator:
        self.trendline = TrendCalculator(
            [candle.openning for candle in self.data],
            self.find_range(),
            [candle.volume for candle in self.data]
        ).do(TrendTypes.DOWN)
        # self.trendline = LowerTrendCalculator(self.data, self.find_range()).do("openning")
        return self
    
    def find_range(self) -> List[int]:
        start = max(0, self.index - self.config.get('convex_length'))
        return range(start, self.index + 1)

    def check_slope(self) -> bool:
        # if self.signal.type is SignalTypes.LONG and self.trendline.p2.subtract(self.trendline.p1).sin() >= self.config.get('min_slope'):
            # return False
        # if self.signal.type is SignalTypes.SHORT and self.trendline.p2.subtract(self.trendline.p1).sin() <= -self.config.get('min_slope'):
            # return False
        return True

    def find_index(self) -> int:
        return self.index + 1
        l1 = LowerTrendCalculator(self.data, self.find_range()).do()
        l2 = UpperTrendCalculator(self.data, self.find_range()).do()
        p = Geometry.intersection(l1, l2)
        if p is None:
            return  -1
        # debug_text('next index of %: %', self.signal.index, math.ceil(p.x))
        return math.ceil(p.x)

    def get_side(self, point: Geometry.Point) -> int:
        return Geometry.side_sign(self.trendline.p1, self.trendline.p2, point)

    def get_trendline_hegiht(self) -> float:
        return math.fabs(self.trendline.p1.y - self.trendline.p2.y)

    def check_passline(self) -> int:
        if self.trendline is None:
            return -1
        # if not self.check_slope() or not self.pass_weight:
        #     return -1
        index = self.find_index()
        reference_point = Geometry.Point(self.index, self.data[self.index].lowest)
        ref_side = self.get_side(reference_point)
        # -1 is so important, because the result still being updated in that candle! -- UPDATED: it's not important anymore
        while index < len(self.data) and index - self.index < self.config.get('signal_life'):
            # p_box_1 = Geometry.Point(index, self.data[index].closing)
            p_box_2 = Geometry.Point(index, self.data[index].openning)
            if ref_side * self.get_side(p_box_2) == -1:
                # self.get_side(reference_point) * self.get_side(p_box_2) == -1:
                return index
            index += 1
        # if index - self.index >= self.config.get('signal_life'):
        #     return -1
        return -1
