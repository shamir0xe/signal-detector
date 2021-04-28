from typing import Any, Dict, List

from ..helpers.config.config_reader import ConfigReader

from .indicator_abstract import Indicator
from ..models.signal import Signal
from ..models.candle import Candle
from ..models.signal_types import SignalTypes
from libs.PythonLibrary.utils import debug_text
from ..helpers.indicators.rsi_calculator import RsiCalculator
from ..helpers.chart.overbought_calculator import OverBoughtCalculator
from ..helpers.chart.oversold_calculator import OverSoldCalculator


class Rsi(Indicator):
    def __init__(self, data: List[Candle]) -> None:
        self.name = 'rsi'
        self.data = data
        self.config = self.__read_config()

    def __read_config(self) -> Dict:
        return ConfigReader('indicators.rsi')
    
    def get_signals(self) -> List[Signal]:
        res = []
        rsi = RsiCalculator(self.data, self.config).calculate()

        up_threshold = self.config.get('upperbound_threshold')
        res = [*res, *self.__short_signals(rsi, up_threshold)]

        lo_threshold = self.config.get('lowerbound_threshold')
        res = [*res, *self.__long_signals(rsi, lo_threshold)]
        return res
    
    def __short_signals(self, rsi: Any, threshold: float) -> List[Signal]:
        res = []
        over_boughts = OverBoughtCalculator().calculate(rsi, threshold=threshold, config=self.config)
        for region in over_boughts:
            for index in region[-1:]:
                res.append(Signal(
                    name = self.name, 
                    type = SignalTypes.SHORT,
                    strength = rsi[index] - threshold,
                    candle = self.data[index],
                    index = index
                ))
        return res

    def __long_signals(self, rsi: Any, threshold: float) -> List[Signal]:
        res = []
        over_boughts = OverSoldCalculator().calculate(rsi, threshold=threshold, config=self.config)
        for region in over_boughts:
            for index in region[-1:]:
                res.append(Signal(
                    name = self.name, 
                    type = SignalTypes.LONG,
                    strength = threshold - rsi[index],
                    candle = self.data[index],
                    index = index
                ))
        return res
