from typing import Any, Dict, List

from .indicator_abstract import Indicator
from ..models.signal import Signal
from ..models.candle import Candle
from ..models.signal_types import SignalTypes
from libs.PythonLibrary.utils import debug_text
from ..helpers.indicators.stoch_calculator import StochCalculator
from ..helpers.chart.overbought_calculator import OverBoughtCalculator
from ..helpers.chart.oversold_calculator import OverSoldCalculator


class Stoch(Indicator):
    def __init__(self, data: List[Candle]) -> None:
        self.name = 'stoch'
        self.data = data
        self.config = self.__read_config()

    def __read_config(self) -> Dict:
        return {
            'upperbound_threshold': 80,
            'lowerbound_threshold': 20,
            'window': 14
        }
    
    def get_signals(self) -> List[Signal]:
        res = []
        stoch = StochCalculator(self.data, self.config).calculate()

        up_threshold = self.config.get('upperbound_threshold', 80)
        res = [*res, *self.__short_signals(stoch, up_threshold)]

        lo_threshold = self.config.get('lowerbound_threshold', 20)
        res = [*res, *self.__long_signals(stoch, lo_threshold)]
        return res
    
    def __short_signals(self, stoch: Any, threshold: float) -> List[Signal]:
        res = []
        over_boughts = OverBoughtCalculator().calculate(stoch, threshold=threshold, config=self.config)
        for region in over_boughts:
            index = region[-1] + 1
            if index >= len(self.data):
                continue
            res.append(Signal(
                name = self.name, 
                type = SignalTypes.SHORT,
                strength = threshold - stoch[index],
                candle = self.data[index],
                index = index
            ))
        return res

    def __long_signals(self, stoch: Any, threshold: float) -> List[Signal]:
        res = []
        over_boughts = OverSoldCalculator().calculate(stoch, threshold=threshold, config=self.config)
        for region in over_boughts:
            index = region[-1] + 1
            if index >= len(self.data):
                continue
            res.append(Signal(
                name = self.name, 
                type = SignalTypes.LONG,
                strength = stoch[index] - threshold,
                candle = self.data[index],
                index = index
            ))
        return res

