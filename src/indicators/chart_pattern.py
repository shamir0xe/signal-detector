from typing import List
from libs.PythonLibrary.geometry import Geometry
from libs.PythonLibrary.utils import debug_text
from src.models.key_level import KeyLevel
from src.helpers.chart.ema_calculator import EmaCalculator
from src.helpers.chart.candlestick_calculator import CandlestickCalculator
from src.helpers.chart.atr_calculator import ATRCalculator
from src.helpers.geometry.line_point_side import LinePointSide
from src.helpers.trend.trend_calculator import TrendCalculator
from src.helpers.time.time_converter import TimeConverter
from src.models.candle import Candle
from src.models.line_sides import LineSides
from src.models.line_slopes import LineSlopes
from src.models.signal import Signal
from src.models.signal_types import SignalTypes
from src.models.trend_types import TrendTypes
from src.indicators.indicator_abstract import Indicator
from src.helpers.config.config_reader import ConfigReader

class ChartPattern(Indicator):
    def __init__(self, data: List[Candle]) -> None:
        self.name = "chart-pattern"
        self.data = data[::]
        self.config = ConfigReader('indicators.chart-pattern')

    def get_signals(self) -> List[Signal]:
        signals = self.__calculate_signals()
        signals = self.__add_limits(signals)
        return signals

    def __calculate_signals(self) -> List[Signal]:
        signals = []
        signals = [*signals, *self.__long_signals()]
        signals = [*signals, *self.__short_signals()]
        return signals
    
    def __long_signals(self) -> List[Signal]:
        """
        calculating long signals with chart patterns strategy  
        """
        signals = []
        for i in range(self.config.get('window') + 1, len(self.data)):
            top_line = self.__top_chart_line(i - 1)
            bl = True
            # top line should be non-increasing
            bl &= self.__get_slope(top_line) is LineSlopes.NEGATIVE
            # the i'th candle should be closed top of the line
            bl &= LinePointSide.do(top_line, Geometry.Point(i, self.data[i].closing)) is LineSides.TOP
            if not bl:
                continue
            # debug_text()
            # debug_text('time: %', TimeConverter.seconds_to_timestamp(self.data[i].time))
            # debug_text('top line: %', top_line)
            # debug_text('slope is: %', self.__get_slope(top_line))
            points, level = CandlestickCalculator(
                data=self.data[i - self.config.get('price-action.left-window'): i + 1],
                key_levels=[KeyLevel(
                    self.data[i - 1].highest, 
                    self.data[i - 1].highest - self.data[i - 1].closing, 
                    i - 1
                )]
            ).do(TrendTypes.DOWN)
            # price action should have occured at i'th candle
            if points == 0 and level is not None:
                # debug_text('We passed!')
                signals.append(Signal(
                    name=self.name,
                    signal_type=SignalTypes.LONG,
                    candle=self.data[i],
                    index=i
                ))
        return signals

    def __get_slope(self, line: Geometry.Line) -> LineSlopes:
        # slope means avg candle size per interval
        slope = (line.p2.y - line.p1.y) / (line.p2.x - line.p1.x)
        # dividing slope by the avg candle size
        slope /= sum([candle.get_size() for candle in self.data[int(line.p1.x):int(line.p2.x)]]) / (line.p2.x - line.p1.x)
        minimum = self.config.get('price-action.ratio')
        if slope < 0:
            if -slope > minimum:
                return LineSlopes.NEGATIVE
        else:
            if slope > minimum:
                return LineSlopes.POSETIVE
        return LineSlopes.HORIZONTAL
    
    def __top_chart_line(self, index: int) -> Geometry.Line:
        return TrendCalculator(
            [candle.highest for candle in self.data],
            range(index - self.config.get('window'), index + 1)
        ).do(TrendTypes.UP)

    def __short_signals(self) -> List[Signal]:
        return []

    def __add_limits(self, signals: List[Signal]) -> List[Signal]:
        res = []
        for signal in signals:
            if signal.type is SignalTypes.LONG:
                delta = ATRCalculator(self.data[:signal.index + 1], {
                    'window': self.config.get('stoploss.window'),
                }).do()[-1] * self.config.get('stoploss.multiplier')
                signal.stop_loss = self.data[signal.index].closing - delta
                signal.take_profit = self.data[signal.index].closing + delta * self.config.get('take-profit.multiplier')
                res.append(signal)
        return res
