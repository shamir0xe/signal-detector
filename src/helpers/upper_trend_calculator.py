import math
from typing import List
from ..models.candle import Candle
from .convex_calculator import UpperBoundConvex
from libs.PythonLibrary.geometry import Geometry
from .show_plot import ShowGeometryPlot


class UpperTrendCalculator:
    def __init__(self, data: List[Candle], index_range: List[int]) -> None:
        self.data = data
        self.index_range = index_range

    def do(self):
        upper_bounds = UpperBoundConvex([Geometry.Point(i, self.data[i].openning) for i in self.index_range]).do()
        index_array = [round(point.x) for point in upper_bounds]
        index_array = index_array[::-1]
        border_lines = [
            [(index_array[i], index_array[i + 1]), 
            math.fabs(sum([self.data[j].volume for j in range(index_array[i], index_array[i + 1])]))]
            for i in range(len(index_array) - 1)
        ]
        border_lines.sort(key=lambda weighted_line: -weighted_line[1])
        # total_volume = sum([ll[1] for ll in border_lines])
        # if border_lines[0][1] / total_volume < self.config.get('min_trend_weight'):
            # self.pass_weight = False
        trend_indices = border_lines[0][0]
        trendline = Geometry.Line(
            Geometry.Point(trend_indices[0], self.data[trend_indices[0]].openning),
            Geometry.Point(trend_indices[1], self.data[trend_indices[1]].openning),
        )
        # ShowGeometryPlot.do([trendline.p1, trendline.p2])
        return trendline

