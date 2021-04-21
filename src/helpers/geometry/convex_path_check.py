from typing import List

from ..trend.trend_calculator import TrendCalculator
from ...models.trend_types import TrendTypes

class ConvexPathCheck:
    def __init__(self, data: List[float], index_range: List[int]) -> None:
        self.data = data
        self.index_range = index_range

    def do(self, trend: TrendTypes) -> bool:
        trendline = TrendCalculator(self.data, self.index_range).do(trend)
        if round(trendline.p1.x) != self.index_range[0]:
            return False
        if round(trendline.p2.x) != self.index_range[-1]:
            return False
        return True
