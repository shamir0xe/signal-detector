from __future__ import annotations
import math

from numpy.core.defchararray import index
from libs.PythonLibrary.utils import debug_text
from math import fabs
from typing import Dict, List

from ..models.signal_types import SignalTypes
from ..models.signal import Signal
from ..models.candle import Candle
from libs.PythonLibrary.geometry import Geometry
from ..helpers.convex_calculator import UpperBoundConvex, LowerBoundConvex
from ..helpers.show_plot import ShowGeometryPlot
from ..helpers.lower_trend_calculator import LowerTrendCalculator
from ..helpers.upper_trend_calculator import UpperTrendCalculator

class TrendlineDelegator:
    def __init__(self, signal: Signal, data: List[Candle]) -> None:
        self.signal = signal
        self.data = data
        self.index = self.signal.index
        self.config = self.__read_config()
        self.trendline = None
        self.pass_weight = True

    def __read_config(self) -> Dict:
        return  {
            'convex_length': 25,
            'signal_life': 25,
            'min_slope': 0.001,
            'min_trend_weight': 0.1
        }

    def downtrend(self) -> TrendlineDelegator:
        self.trendline = UpperTrendCalculator(self.data, self.find_range()).do()
        return self

    def uptrend(self) -> TrendlineDelegator:
        self.trendline = LowerTrendCalculator(self.data, self.find_range()).do()
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
        return self.index + 5
        l1 = LowerTrendCalculator(self.data, self.find_range()).do()
        l2 = UpperTrendCalculator(self.data, self.find_range()).do()
        p = Geometry.intersection(l1, l2)
        if p is None:
            return  -1
        debug_text('next index of %: %', self.signal.index, math.ceil(p.x))
        return math.ceil(p.x)

    def check_passline(self) -> int:
        if self.trendline is None:
            return 0
        if not self.check_slope() or not self.pass_weight:
            return -1
        index = self.find_index()
        while index < len(self.data) and index - self.index < self.config.get('signal_life'):
            if Geometry.side_sign(self.trendline.p1, self.trendline.p2, Geometry.Point(index, self.data[index].closing)) * \
                Geometry.side_sign(self.trendline.p1, self.trendline.p2, Geometry.Point(self.index, self.data[self.index].closing)) == -1:
                return index
            index += 1
        if index - self.index >= self.config.get('signal_life'):
            return -1
        return 0
