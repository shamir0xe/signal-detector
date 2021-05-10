from __future__ import annotations
from libs.PythonLibrary.geometry import Geometry
from typing import Dict, List
from src.helpers.geometry.convex_calculator import ConvexBound
from src.models.trend_types import TrendTypes


class TrendConfirmator:
    def __init__(self, data: List[float], config: Dict) -> None:
        self.data = data
        self.config = config

    def calculate_bounds(self, trend: TrendTypes) -> TrendConfirmator:
        self.bounds = ConvexBound([
            Geometry.Point(i, self.data[i]) for i in range(self.__start(), len(self.data))
        ]).do(trend)
        self.bounds = self.bounds[::-1]
        return self

    def check(self) -> bool:
        return self.bounds[-1].y > self.bounds[-2].y + 1e-9

    def trend_slope(self) -> float:
        return (self.bounds[-1].y - self.bounds[-2].y) / (self.bounds[-1].x - self.bounds[-2].x)

    def __start(self) -> int:
        return max(0, len(self.data) - self.config.get('window'))
