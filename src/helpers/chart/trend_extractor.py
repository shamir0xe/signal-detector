from src.helpers.geometry.convex_calculator import ConvexBound
from src.facades.config import Config
from libs.PythonLibrary.utils import debug_text
from libs.PythonLibrary.geometry import Geometry
from typing import List
from src.helpers.trend.trend_calculator import TrendCalculator

from src.models.candle import Candle
from src.models.trend_types import TrendTypes


class TrendExtractor:
    def __init__(
        self,
        data: List[Candle]
    ) -> None:
        self.data = data[:-1]

    def do(self) -> TrendTypes:
        sz = len(self.data)

        line_top = TrendCalculator([candle.highest for candle in self.data], range(sz)).do(trend=TrendTypes.UP)
        line_bot = TrendCalculator([candle.lowest for candle in self.data], range(sz)).do(trend=TrendTypes.DOWN)

        # line_top = self.trend([candle.highest for candle in self.data], TrendTypes.UP)
        # line_bot = self.trend([candle.lowest for candle in self.data], TrendTypes.DOWN)
        candle_avg = sum([candle.get_size() for candle in self.data]) / len(self.data)
        candle_avg *= Config.get('helpers.trend.candle-avg-multiplier')
        slope_top = -1 if self.get_height(line_top) < -candle_avg else +1 if \
            self.get_height(line_top) > +candle_avg else 0
        slope_bot = -1 if self.get_height(line_bot) < -candle_avg else +1 if \
            self.get_height(line_bot) > +candle_avg else 0
        # debug_text('top-line: %', line_top)
        # debug_text('bot-line: %', line_bot)
        # debug_text('SLOPES: %, %', slope_top, slope_bot)
        acc = slope_top + slope_bot
        if acc == -2:
            return TrendTypes.DOWN
        if acc == +2:
            return TrendTypes.UP
        return TrendTypes.HORIZONTAL
    
    def get_height(self, line: Geometry.Line) -> float:
        return line.p2.y - line.p1.y
    
    def trend(self, data: List[float], trend: TrendTypes) -> Geometry.Line:
        bounds = ConvexBound([
            Geometry.Point(i, data[i]) for i in 
            range(len(data) - 10, len(data))]
        ).do(trend)
        bounds = bounds[::-1]
        return Geometry.Line(
            bounds[-2],
            bounds[-1]
        )
        

