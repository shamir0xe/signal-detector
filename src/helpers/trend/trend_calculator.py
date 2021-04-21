import math
from typing import List, Optional
from libs.PythonLibrary.geometry import Geometry
from ..geometry.convex_calculator import ConvexBound
from ..geometry.show_plot import ShowGeometryPlot
from ...models.trend_types import TrendTypes
from ...models.candle import Candle


class TrendCalculator:
    def __init__(self, data: List[float], index_range: List[int], volume: Optional[List[float]] = None) -> None:
        self.data = data
        self.index_range = index_range
        self.volume = volume if volume is not None else [1 for _ in range(len(data))]

    def do(self, trend: TrendTypes):
        bounds = ConvexBound([Geometry.Point(i, self.data[i]) for i in self.index_range]).do(trend)
        index_array = [round(point.x) for point in bounds]
        index_array = index_array[::-1]
        border_lines = [
            [(index_array[i], index_array[i + 1]), 
            math.fabs(sum([self.volume[j] for j in range(index_array[i], index_array[i + 1])]))]
            for i in range(len(index_array) - 1)
        ]
        border_lines.sort(key=lambda weighted_line: -weighted_line[1])
        trend_indices = border_lines[0][0]
        trendline = Geometry.Line(
            Geometry.Point(trend_indices[0], self.data[trend_indices[0]]),
            Geometry.Point(trend_indices[1], self.data[trend_indices[1]]),
        )
        # ShowGeometryPlot.do([trendline.p1, trendline.p2])
        return trendline

